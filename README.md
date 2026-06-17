# Get Started
To get started and build the feature set, first install the required packages using the following command in terminal
pip install -r requirements.txt

Then run download_noaa_lcd.py, rainfall_loader.py, and build_feature_store_v1.py in that order
python src/FIELNAME.py

At this point, if you open data/raw and data/processed you will see the raw downloaded files and feature set respectively.

See below for documentation on methodlogy, assumptions, and next steps.

# North River WRRF Feature Store

This repo builds a local hourly external-forcing feature store for future North River WRRF influent-flow modeling.

The current work is data preparation only. I am not training a model yet because I do not have real hourly North River influent-flow target data. The Version 1 feature store is meant to become the external-driver side of a future model table.

## Current Status

Version 1 has been built locally:

- `data/processed/north_river_feature_store_v1.parquet`
- `data/processed/north_river_feature_store_v1.csv`

Those outputs are intentionally ignored by Git. They can be regenerated locally from the scripts in `src/`.

## Why This Exists

Influent flow is one of the basic design and operating quantities for a wastewater treatment facility. It affects hydraulic loading, wet-weather capacity, plant operations, and planning assumptions. For North River WRRF, future inflow response may reflect rainfall, sewer-system storage and routing, dry-weather patterns, and possibly Hudson River tide conditions.

This is not a generic weather-prediction project. Rainfall does not become plant influent instantly, and the sewer system can delay, store, and route flow before it reaches the plant. The goal of this first version is to prepare the external features that can later be joined to real hourly plant flow data.

I have not picked a final forecast horizon yet. Once hourly influent-flow data is available, useful horizons will probably include short wet-weather lead times, such as the next few hours through about 24-48 hours. The right horizon should be set based on the modeling goal and how the target data is reported.

## How The Columns Were Chosen

The columns came from a mix of DEP report review, source availability, and basic hydrologic reasoning:

- DEP InfoWorks Citywide Recalibration Report: rainfall source choice should follow the modeling/calibration context, not just convenience.
- DEP Hydraulic Capacity Analysis Report: storage, travel time, and wet-weather hydraulic response matter, so lagged and rolling rainfall features are useful starting points.
- North River Appendix G: requested via FOIL and deferred until available.
- NOAA CO-OPS tide data: included because North River is next to the Hudson River and tide may be useful context.

The detailed source decisions are in `docs/source_register.md`. The final column reference is in `docs/data_dictionary.md`.

DEP source documents reviewed:

- [InfoWorks Citywide Recalibration Report](https://www.nyc.gov/assets/dep/downloads/pdf/water/nyc-waterways/citywide-ltcp/infoworks-citywide-recalibration-report.pdf)
- [Hydraulic Capacity Analysis Report, 2012](https://www.nyc.gov/assets/dep/downloads/pdf/water/nyc-waterways/citywide-ltcp/hydraulic-capacity-analysis-report-2012.pdf)

## Version 1 Sources

Rainfall:

- Preferred conceptually: NRCC / Cornell Central Park rainfall, because it aligns with DEP/North River calibration context.
- Practical fallback used in V1: NOAA LCD Central Park station `USW00094728`.

I checked the NRCC gauge page, CLIMOD 2, and ACIS first. Those routes either were not straightforward to automate or did not provide a confirmed hourly Central Park precipitation export. NOAA LCD was used as the practical fallback because it provides Central Park hourly observations in downloadable yearly files. The loader uses regular `FM-15` hourly observations, buckets the usual `:51` observation timestamp to the hour, treats trace precipitation as `0.0 mm`, and keeps missing rainfall missing.

Tide / water level:

- NOAA CO-OPS Station `8518750`, The Battery.
- Product: hourly height.
- Datum: `MLLW`.
- Units: metric.
- Time convention: `lst_ldt` local station time.

The Battery is a tide proxy, not a plant-specific hydraulic boundary condition. It is included because North River is near the Hudson River and water level may be useful context in later modeling.

## What V1 Contains

The feature store has a complete hourly backbone from:

- `2015-01-01 00:00`
- through `2024-12-31 23:00`

It includes:

- calendar features
- Central Park rainfall
- rainfall lags
- rolling rainfall totals and maxima
- storm and antecedent wetness features
- Battery water level
- tide lags, changes, rolling means, and tidal phase features
- source labels, units, datum, and missing-data flags

## What V1 Does Not Contain

Version 1 does not include:

- model training
- synthetic influent flow
- `influent_flow_mgd`
- target-flow columns
- flow-lag features
- cloud, Docker, database, Airflow, dashboard, or enterprise feature-store tooling

## Rebuild Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the NOAA LCD fallback rainfall file:

```bash
python3 src/download_noaa_lcd.py
```

Build the V1 feature store:

```bash
python3 src/build_feature_store_v1.py
```

The raw and processed data files are ignored by Git by default.

## Inspect Locally

Use the notebook below to inspect the generated feature store:

```text
notebooks/inspect_feature_store_v1.ipynb
```

The notebook is for local QA only. It does not train a model or assume a flow target.

## Documentation

- `docs/project_log.md`: concise build and decision log
- `docs/source_register.md`: source choices and limitations
- `docs/data_dictionary.md`: V1 column reference
- `docs/methodology_outline.md`: public methodology notes

## Next Step

The next major step is to obtain actual hourly North River influent-flow data. After that, the project can build `north_river_model_table_v1` by joining real flow observations to this external-forcing feature store.

For a concise Phase 1 summary, see [`docs/status_update_v1.md`](docs/status_update_v1.md).
