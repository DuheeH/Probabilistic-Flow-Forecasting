# North River WRRF Feature Store

Local data science project for building an hourly external-forcing feature store for North River WRRF influent-flow forecasting research.

## Immediate Goal

Build Version 1 external-forcing datasets:

- `data/processed/north_river_feature_store_v1.parquet`
- `data/processed/north_river_feature_store_v1.csv`

Version 1 should include rainfall, tide or water level, calendar features, rainfall lags, rolling rainfall, tide lags, tidal harmonic features, source metadata, and missing-data flags.

## Scope Rules

- Do not train a model yet.
- Do not create synthetic North River influent flow.
- Do not create target-flow columns until real hourly North River influent-flow data is available.
- Keep external-forcing features separate from future model-target data.
- Keep this local and lightweight: no cloud, Docker, databases, Airflow, dashboards, or enterprise feature-store tooling.

## Project Layout

```text
data/raw/          Original source files and downloaded inputs
data/processed/    Cleaned feature-store outputs
docs/              Data dictionary, source register, and project log
src/               Reusable Python code when the build script is added
```

## Primary Version 1 Sources

- Rainfall: Cornell NRCC NYC Weather Network / Central Park gauge.
- Tide / water level: NOAA CO-OPS Station 8518750, The Battery.
- Optional temperature: NOAA Local Climatological Data if easy.

Schema and source notes are tracked in `docs/data_dictionary.md` and `docs/source_register.md`.
