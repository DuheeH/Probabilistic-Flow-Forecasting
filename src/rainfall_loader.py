"""Load and standardize approved Central Park rainfall source files.

The loader is intentionally conservative:

- It only searches explicitly documented raw file paths.
- It does not assume missing rainfall is zero.
- It refuses to guess units when units are unclear.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl


NRCC_CLIMOD2_RAINFALL_PATH = Path(
    "data/raw/weather/central_park_nrcc_climod2_hourly_rainfall_2015_2024.csv"
)
NOAA_LCD_RAINFALL_PATH = Path(
    "data/raw/weather/central_park_noaa_lcd_hourly_weather_2015_2024.csv"
)

TIMESTAMP_COLUMN_CANDIDATES = (
    "timestamp",
    "datetime",
    "date_time",
    "date time",
    "valid",
    "valid_time",
    "valid time",
    "date",
)

DATE_COLUMN_CANDIDATES = ("date", "day")
TIME_COLUMN_CANDIDATES = ("time", "hour")

RAIN_COLUMN_CANDIDATES = (
    "rain_mm",
    "rain",
    "hourlyprecipitation",
    "hourly precipitation",
    "precipitation",
    "precip",
    "pcpn",
    "prcp",
)

SOURCE_CONFIGS = (
    {
        "path": NRCC_CLIMOD2_RAINFALL_PATH,
        "source": "NRCC/Cornell CLIMOD 2 Central Park hourly rainfall",
        "units": None,
    },
    {
        "path": NOAA_LCD_RAINFALL_PATH,
        "source": "NOAA/NCEI LCD fallback: Central Park hourly weather",
        "units": "mm",
    },
)


def _normalize_name(value: str) -> str:
    return value.lower().strip().replace("_", " ").replace("-", " ")


def _normalized_columns(df: pl.DataFrame) -> dict[str, str]:
    return {_normalize_name(col): col for col in df.columns}


def _find_column(df: pl.DataFrame, candidates: tuple[str, ...]) -> str | None:
    normalized = _normalized_columns(df)
    normalized_candidates = tuple(_normalize_name(candidate) for candidate in candidates)
    for candidate in normalized_candidates:
        if candidate in normalized:
            return normalized[candidate]
    for key, original in normalized.items():
        if any(candidate in key for candidate in normalized_candidates):
            return original
    return None


def _detect_rain_units(column_name: str) -> str | None:
    name = column_name.lower()
    if "mm" in name or "millimeter" in name:
        return "mm"
    if "inch" in name or "in." in name or name.endswith("_in") or name.endswith(" in"):
        return "inch"
    return None


def _with_timestamp(df: pl.DataFrame) -> pl.DataFrame:
    timestamp_col = _find_column(df, TIMESTAMP_COLUMN_CANDIDATES)
    if timestamp_col is not None:
        return df.with_columns(
            pl.col(timestamp_col).cast(pl.Utf8).str.to_datetime(strict=False).alias("timestamp")
        )

    date_col = _find_column(df, DATE_COLUMN_CANDIDATES)
    time_col = _find_column(df, TIME_COLUMN_CANDIDATES)
    if date_col is None:
        raise ValueError("Could not find a timestamp/date column in the rainfall file.")
    if time_col is None:
        return df.with_columns(
            pl.col(date_col).cast(pl.Utf8).str.to_datetime(strict=False).alias("timestamp")
        )

    return df.with_columns(
        (pl.col(date_col).cast(pl.Utf8) + " " + pl.col(time_col).cast(pl.Utf8))
        .str.to_datetime(strict=False)
        .alias("timestamp")
    )


def _rain_expr(rain_col: str, units: str) -> pl.Expr:
    raw = pl.col(rain_col).cast(pl.Utf8).str.strip_chars()
    numeric_text = (
        pl.when(raw.str.to_uppercase() == "T")
        .then(pl.lit("0"))
        .otherwise(raw.str.replace_all(r"[^0-9.\-]", ""))
    )
    rain = numeric_text.cast(pl.Float64, strict=False)
    if units == "inch":
        rain = rain * 25.4
    return rain.cast(pl.Float32)


def load_rainfall_file(
    path: str | Path,
    *,
    source: str,
    units: str | None = None,
) -> pl.DataFrame:
    """Load one approved rainfall CSV and standardize it."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Rainfall file not found: {path}")

    df = pl.read_csv(path, infer_schema_length=1000, ignore_errors=False)
    df = _with_timestamp(df)

    rain_col = _find_column(df, RAIN_COLUMN_CANDIDATES)
    if rain_col is None:
        raise ValueError("Could not find a precipitation/rainfall column in the rainfall file.")

    detected_units = units or _detect_rain_units(rain_col)
    if detected_units is None:
        raise ValueError(
            "Could not determine rainfall units from the file. Re-run with explicit "
            "units='mm' or units='inch' after confirming the export units."
        )
    if detected_units not in {"mm", "inch"}:
        raise ValueError("Rainfall units must be either 'mm' or 'inch'.")

    out = df.select(
        pl.col("timestamp"),
        _rain_expr(rain_col, detected_units).alias("rain_mm"),
    ).with_columns(
        pl.col("rain_mm").is_null().cast(pl.Int8).alias("rain_missing_flag"),
        pl.lit(source).alias("rain_source"),
    ).sort("timestamp")

    if out["timestamp"].null_count() > 0:
        raise ValueError("Some rainfall timestamps could not be parsed.")

    return out


def load_central_park_rainfall() -> pl.DataFrame:
    """Load Central Park rainfall using the approved source search order."""

    searched = []
    for config in SOURCE_CONFIGS:
        path = config["path"]
        searched.append(str(path))
        if path.exists():
            return load_rainfall_file(
                path,
                source=config["source"],
                units=config["units"],
            )

    raise FileNotFoundError(
        "No approved Central Park rainfall file found. Searched: " + ", ".join(searched)
    )
