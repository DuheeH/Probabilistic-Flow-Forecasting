# Project Log

This is a working log for the North River WRRF influent-flow feature-store project. The goal is to keep track of what was tried, what was selected, and what still needs to be checked later.

## Project Goal

The immediate goal is to build a Version 1 hourly external-forcing feature store for future North River WRRF influent-flow modeling.

Version 1 is not a model table. It does not include real influent flow, synthetic influent flow, target columns, or flow-lag features. I built this first because I do not have the real hourly influent-flow target yet.

Final local outputs:

- `data/processed/north_river_feature_store_v1.parquet`
- `data/processed/north_river_feature_store_v1.csv`

These outputs are generated locally and are not committed to Git.

## Source Investigation

### Rainfall

Central Park rainfall was the preferred conceptual starting point because DEP/North River calibration context points toward Central Park / CPK rainfall. It is a point-gauge assumption, not a claim that Central Park perfectly represents rainfall over the whole North River drainage area.

The source path was checked in this order:

1. NRCC NYC Weather Network / Central Park gauge
   - Preferred conceptually.
   - The gauge page was not straightforward to automate for a decade of hourly rainfall.

2. CLIMOD 2
   - Checked as a possible NRCC/Cornell path.
   - Central Park metadata was found.
   - A confirmed hourly precipitation export was not found.

3. ACIS / NOAA Regional Climate Centers
   - Confirmed Central Park metadata and daily precipitation.
   - Tested hourly-style precipitation requests did not produce a usable hourly endpoint.

4. NOAA LCD
   - Approved as the explicit practical fallback.
   - Station used: Central Park `USW00094728`.
   - Raw file saved locally as:
     `data/raw/weather/central_park_noaa_lcd_hourly_weather_2015_2024.csv`

NOAA LCD rainfall handling:

- Use regular `FM-15` hourly observations only.
- Observations usually occur near `:51`.
- Timestamps are bucketed down to the corresponding hour.
- `HourlyPrecipitation` is treated as millimeters based on NOAA LCDv2 bulk CSV documentation.
- Trace precipitation (`T`) is treated as `0.0 mm`.
- Missing rainfall is not filled with zero.

### Tide / Water Level

NOAA CO-OPS Station `8518750`, The Battery, was selected as the Version 1 tide proxy.

Raw tide file:

- `data/raw/tides/battery_noaa_coops_hourly_height_2015_2024_mllw_metric_lst_ldt.csv`

Tide settings:

- product: hourly height
- datum: `MLLW`
- units: metric
- time zone request: `lst_ldt`

The Battery is a useful lower-Hudson/New York Harbor proxy, but it is not a plant-specific hydraulic boundary condition.

## Timestamp and Time Zone Assumptions

Version 1 does not use UTC internally.

The final `timestamp` column is stored as naive local time aligned to New York/source-station local time. The feature store uses a complete naive hourly backbone from `2015-01-01 00:00` through `2024-12-31 23:00`.

Rainfall and tide are left-joined onto that backbone.

Timestamp handling:

- NOAA LCD rainfall `FM-15` observations are bucketed down to the local hour.
- NOAA CO-OPS Battery tide data was requested using `time_zone=lst_ldt`.
- The final V1 timestamps are naive local hourly timestamps.

Known limitation:

- Daylight-saving-time handling is not fully modeled in V1.
- The backbone does not explicitly represent nonexistent spring-forward hours or repeated fall-back hours.
- A future version may standardize fully to UTC once source and target timestamp conventions are confirmed.

## Final V1 Build Result

Build script:

- `src/build_feature_store_v1.py`

Outputs:

- `data/processed/north_river_feature_store_v1.parquet`
- `data/processed/north_river_feature_store_v1.csv`

Validation summary:

| Check | Result |
| --- | --- |
| Start timestamp | `2015-01-01 00:00:00` |
| End timestamp | `2024-12-31 23:00:00` |
| Rows | 87,672 |
| Expected hourly rows | 87,672 |
| Duplicate timestamps | 0 |
| Missing timestamps | 0 |
| Missing rainfall values | 1,245 |
| Missing tide values | 10 |
| Forbidden flow/target columns | none |

Source labels in the output:

- `rain_source`: `NOAA NCEI LCD Central Park USW00094728 fallback`
- `tide_source`: `NOAA CO-OPS 8518750 The Battery`
- `water_level_units`: `metric`
- `water_level_datum`: `MLLW`

## What V1 Contains

The V1 feature store includes:

- calendar features
- rainfall values, lags, rolling totals, rolling maxima
- storm duration and storm rainfall features
- 3-day and 7-day antecedent wetness indexes
- Battery water level, lags, changes, and rolling means
- simple tidal harmonic features
- source metadata and missing-data flags

## What V1 Excludes

Version 1 intentionally excludes:

- model training
- synthetic North River influent flow
- `influent_flow_mgd`
- flow-lag features
- target-flow columns
- cloud/database/orchestration/dashboard tooling

## Limitations

- Central Park rainfall is a point-gauge fallback, not sewershed-average rainfall.
- The Battery is a tide proxy, not a plant-specific boundary condition.
- North River Appendix G is not available yet.
- Real hourly North River influent-flow data is not available yet.
- V1 uses naive local timestamps, with daylight-saving-time handling left as a known limitation.

## Next Steps

1. Obtain real hourly North River influent-flow data.
2. Confirm its timestamp convention.
3. Build `north_river_model_table_v1` by joining real flow observations to the external-forcing feature store.
4. Only then start baseline model training.
