"""Build the Version 1 North River external-forcing feature store.

Version 1 intentionally excludes influent-flow targets, flow lags, model
training, and synthetic target data.
"""

from __future__ import annotations

import math
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import polars as pl

from rainfall_loader import NOAA_LCD_SOURCE, load_central_park_rainfall


START = datetime(2015, 1, 1, 0)
END = datetime(2024, 12, 31, 23)

TIDE_RAW_PATH = Path(
    "data/raw/tides/battery_noaa_coops_hourly_height_2015_2024_mllw_metric_lst_ldt.csv"
)
PARQUET_OUTPUT = Path("data/processed/north_river_feature_store_v1.parquet")
CSV_OUTPUT = Path("data/processed/north_river_feature_store_v1.csv")

TIDE_SOURCE = "NOAA CO-OPS 8518750 The Battery"
WATER_LEVEL_UNITS = "metric"
WATER_LEVEL_DATUM = "MLLW"
TIDE_TIME_ZONE = "lst_ldt"


def hourly_backbone(start: datetime = START, end: datetime = END) -> pl.DataFrame:
    timestamps = []
    current = start
    while current <= end:
        timestamps.append(current)
        current += timedelta(hours=1)
    return pl.DataFrame({"timestamp": timestamps})


def coops_url(year: int) -> str:
    return (
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
        f"?begin_date={year}0101"
        f"&end_date={year}1231"
        "&station=8518750"
        "&product=hourly_height"
        f"&datum={WATER_LEVEL_DATUM}"
        f"&time_zone={TIDE_TIME_ZONE}"
        f"&units={WATER_LEVEL_UNITS}"
        "&format=csv"
        "&application=north_river_wrrf"
    )


def download_text(url: str) -> str:
    result = subprocess.run(
        ["curl", "-fsL", url],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.stdout


def ensure_tide_raw_file(path: Path = TIDE_RAW_PATH) -> Path:
    if path.exists() and path.stat().st_size > 0:
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    wrote_header = False
    with path.open("w", encoding="utf-8", newline="") as out:
        for year in range(START.year, END.year + 1):
            url = coops_url(year)
            print(f"Downloading tide {year}: {url}")
            lines = download_text(url).splitlines()
            if not lines:
                raise ValueError(f"No tide data returned for {year}")
            if not wrote_header:
                out.write(lines[0] + "\n")
                wrote_header = True
            for line in lines[1:]:
                out.write(line + "\n")
    return path


def load_tide(path: Path = TIDE_RAW_PATH) -> pl.DataFrame:
    path = ensure_tide_raw_file(path)
    df = pl.read_csv(path, infer_schema_length=0, ignore_errors=False)
    required = {"Date Time", " Water Level"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Tide file is missing required columns: {sorted(missing)}")

    out = (
        df.select(
            pl.col("Date Time").str.to_datetime("%Y-%m-%d %H:%M", strict=False).alias("timestamp"),
            pl.col(" Water Level").cast(pl.Float32, strict=False).alias("water_level"),
        )
        .group_by("timestamp", maintain_order=True)
        .agg(pl.col("water_level").last())
        .with_columns(
            pl.col("water_level").is_null().cast(pl.Int8).alias("tide_missing_flag"),
            pl.lit(TIDE_SOURCE).alias("tide_source"),
            pl.lit(WATER_LEVEL_UNITS).alias("water_level_units"),
            pl.lit(WATER_LEVEL_DATUM).alias("water_level_datum"),
        )
        .sort("timestamp")
    )

    if out["timestamp"].null_count() > 0:
        raise ValueError("Some tide timestamps could not be parsed.")
    return out


def complete_rolling_sum(col: str, window: int, alias: str) -> pl.Expr:
    shifted = pl.col(col).shift(1)
    null_count = shifted.is_null().cast(pl.Int16).rolling_sum(
        window_size=window,
        min_samples=window,
    )
    value = shifted.fill_null(0).rolling_sum(window_size=window, min_samples=window)
    return (
        pl.when(null_count == 0)
        .then(value)
        .otherwise(None)
        .cast(pl.Float32)
        .alias(alias)
    )


def complete_rolling_max(col: str, window: int, alias: str) -> pl.Expr:
    shifted = pl.col(col).shift(1)
    null_count = shifted.is_null().cast(pl.Int16).rolling_sum(
        window_size=window,
        min_samples=window,
    )
    value = shifted.rolling_max(window_size=window, min_samples=window)
    return (
        pl.when(null_count == 0)
        .then(value)
        .otherwise(None)
        .cast(pl.Float32)
        .alias(alias)
    )


def complete_rolling_mean(col: str, window: int, alias: str) -> pl.Expr:
    shifted = pl.col(col).shift(1)
    null_count = shifted.is_null().cast(pl.Int16).rolling_sum(
        window_size=window,
        min_samples=window,
    )
    value = shifted.rolling_mean(window_size=window, min_samples=window)
    return (
        pl.when(null_count == 0)
        .then(value)
        .otherwise(None)
        .cast(pl.Float32)
        .alias(alias)
    )


def antecedent_wetness(values: list[float | None], span_hours: int) -> list[float | None]:
    alpha = 2 / (span_hours + 1)
    out: list[float | None] = []
    previous: float | None = None
    for value in values:
        out.append(previous)
        if value is None:
            previous = None
        elif previous is None:
            previous = float(value)
        else:
            previous = alpha * float(value) + (1 - alpha) * previous
    return out


def storm_features(values: list[float | None], wet_threshold_mm: float = 0.1) -> dict[str, list]:
    duration: list[int | None] = []
    total: list[float | None] = []
    since: list[int | None] = []
    current_duration = 0
    current_total = 0.0
    hours_since: int | None = None

    for value in values:
        if value is None:
            duration.append(None)
            total.append(None)
            since.append(hours_since)
            current_duration = 0
            current_total = 0.0
            if hours_since is not None:
                hours_since += 1
            continue

        if value > wet_threshold_mm:
            current_duration += 1
            current_total += value
            hours_since = 0
        else:
            current_duration = 0
            current_total = 0.0
            if hours_since is not None:
                hours_since += 1

        duration.append(current_duration)
        total.append(current_total)
        since.append(hours_since)

    return {
        "storm_duration": duration,
        "storm_total_rainfall": total,
        "hours_since_last_rain": since,
    }


def add_calendar_features(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("timestamp").dt.hour().cast(pl.Int8).alias("hour_of_day"),
        pl.col("timestamp").dt.weekday().sub(1).cast(pl.Int8).alias("day_of_week"),
        pl.col("timestamp").dt.month().cast(pl.Int8).alias("month"),
    ).with_columns(
        (pl.col("day_of_week") >= 5).cast(pl.Int8).alias("is_weekend"),
        (2 * math.pi * pl.col("hour_of_day") / 24).sin().cast(pl.Float32).alias("hour_sin"),
        (2 * math.pi * pl.col("hour_of_day") / 24).cos().cast(pl.Float32).alias("hour_cos"),
        (2 * math.pi * pl.col("day_of_week") / 7).sin().cast(pl.Float32).alias("dow_sin"),
        (2 * math.pi * pl.col("day_of_week") / 7).cos().cast(pl.Float32).alias("dow_cos"),
        (2 * math.pi * (pl.col("month") - 1) / 12).sin().cast(pl.Float32).alias("month_sin"),
        (2 * math.pi * (pl.col("month") - 1) / 12).cos().cast(pl.Float32).alias("month_cos"),
    )


def build_feature_store() -> pl.DataFrame:
    backbone = hourly_backbone()
    rainfall = load_central_park_rainfall()
    tide = load_tide()

    df = (
        backbone.join(rainfall, on="timestamp", how="left")
        .join(tide, on="timestamp", how="left")
        .with_columns(
            pl.col("rain_missing_flag").fill_null(1).cast(pl.Int8),
            pl.col("tide_missing_flag").fill_null(1).cast(pl.Int8),
            pl.col("rain_source").fill_null(NOAA_LCD_SOURCE),
            pl.col("tide_source").fill_null(TIDE_SOURCE),
            pl.col("water_level_units").fill_null(WATER_LEVEL_UNITS),
            pl.col("water_level_datum").fill_null(WATER_LEVEL_DATUM),
        )
    )
    df = add_calendar_features(df)

    elapsed_hours = pl.col("timestamp").sub(pl.lit(START)).dt.total_hours()
    df = df.with_columns(
        pl.col("rain_mm").alias("rain_t"),
        pl.col("rain_mm").shift(1).alias("rain_t_1"),
        pl.col("rain_mm").shift(3).alias("rain_t_3"),
        pl.col("rain_mm").shift(6).alias("rain_t_6"),
        pl.col("rain_mm").shift(12).alias("rain_t_12"),
        pl.col("rain_mm").shift(24).alias("rain_t_24"),
        pl.col("water_level").shift(1).alias("water_level_t_1"),
        pl.col("water_level").shift(6).alias("water_level_t_6"),
        (pl.col("water_level") - pl.col("water_level").shift(1)).alias("water_level_change_1h"),
        (pl.col("water_level") - pl.col("water_level").shift(3)).alias("water_level_change_3h"),
        (2 * math.pi * elapsed_hours / 12.42).sin().cast(pl.Float32).alias("tidal_phase_sin"),
        (2 * math.pi * elapsed_hours / 12.42).cos().cast(pl.Float32).alias("tidal_phase_cos"),
    )

    rolling_exprs = []
    for window, alias in [
        (6, "rain_last_6h"),
        (12, "rain_last_12h"),
        (24, "rain_last_24h"),
        (72, "rain_last_72h"),
    ]:
        rolling_exprs.append(complete_rolling_sum("rain_mm", window, alias))
    for window, alias in [(6, "rain_max_last_6h"), (24, "rain_max_last_24h")]:
        rolling_exprs.append(complete_rolling_max("rain_mm", window, alias))
    for window, alias in [
        (6, "water_level_rolling_mean_6h"),
        (24, "water_level_rolling_mean_24h"),
    ]:
        rolling_exprs.append(complete_rolling_mean("water_level", window, alias))

    df = df.with_columns(rolling_exprs)

    rain_values = df["rain_mm"].to_list()
    storm = storm_features(rain_values)
    df = df.with_columns(
        pl.Series("AWI_3d", antecedent_wetness(rain_values, 72), dtype=pl.Float32),
        pl.Series("AWI_7d", antecedent_wetness(rain_values, 168), dtype=pl.Float32),
        pl.Series("storm_duration", storm["storm_duration"], dtype=pl.Int16),
        pl.Series("storm_total_rainfall", storm["storm_total_rainfall"], dtype=pl.Float32),
        pl.Series("hours_since_last_rain", storm["hours_since_last_rain"], dtype=pl.Int16),
    )

    ordered_columns = [
        "timestamp",
        "hour_of_day",
        "day_of_week",
        "month",
        "is_weekend",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
        "month_sin",
        "month_cos",
        "rain_mm",
        "rain_t",
        "rain_t_1",
        "rain_t_3",
        "rain_t_6",
        "rain_t_12",
        "rain_t_24",
        "rain_last_6h",
        "rain_last_12h",
        "rain_last_24h",
        "rain_last_72h",
        "rain_max_last_6h",
        "rain_max_last_24h",
        "storm_duration",
        "storm_total_rainfall",
        "hours_since_last_rain",
        "AWI_3d",
        "AWI_7d",
        "water_level",
        "water_level_t_1",
        "water_level_t_6",
        "water_level_change_1h",
        "water_level_change_3h",
        "water_level_rolling_mean_6h",
        "water_level_rolling_mean_24h",
        "tidal_phase_sin",
        "tidal_phase_cos",
        "rain_missing_flag",
        "tide_missing_flag",
        "rain_source",
        "tide_source",
        "water_level_units",
        "water_level_datum",
    ]
    return df.select(ordered_columns)


def validate(df: pl.DataFrame) -> dict[str, object]:
    expected_rows = int((END - START).total_seconds() / 3600) + 1
    forbidden = [
        col
        for col in df.columns
        if col == "influent_flow_mgd" or col.startswith("flow_")
    ]
    duplicate_timestamps = df.height - df.select("timestamp").n_unique()
    missing_timestamps = expected_rows - df.height
    return {
        "start_timestamp": df.select("timestamp").min().item(),
        "end_timestamp": df.select("timestamp").max().item(),
        "rows": df.height,
        "expected_rows": expected_rows,
        "duplicate_timestamps": duplicate_timestamps,
        "missing_timestamps": missing_timestamps,
        "missing_rainfall_values": df.select("rain_mm").null_count().item(),
        "missing_tide_values": df.select("water_level").null_count().item(),
        "rainfall_source_range": df.select("rain_source").unique().to_series().to_list(),
        "tide_source_range": df.select("tide_source").unique().to_series().to_list(),
        "forbidden_columns": forbidden,
        "columns": df.columns,
    }


def write_outputs(df: pl.DataFrame) -> None:
    PARQUET_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(PARQUET_OUTPUT)
    df.write_csv(CSV_OUTPUT)


def main() -> None:
    df = build_feature_store()
    summary = validate(df)
    if summary["rows"] != summary["expected_rows"]:
        raise ValueError(f"Unexpected row count: {summary}")
    if summary["duplicate_timestamps"] != 0 or summary["missing_timestamps"] != 0:
        raise ValueError(f"Timestamp validation failed: {summary}")
    if summary["forbidden_columns"]:
        raise ValueError(f"Forbidden columns found: {summary['forbidden_columns']}")

    write_outputs(df)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print(f"parquet_output: {PARQUET_OUTPUT}")
    print(f"csv_output: {CSV_OUTPUT}")


if __name__ == "__main__":
    main()
