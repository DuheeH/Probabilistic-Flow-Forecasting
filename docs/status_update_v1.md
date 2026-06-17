# North River WRRF Feature Store V1 Status Update

## Project Purpose

This project is preparing the data foundation for a future North River WRRF influent-flow forecasting model. The current work is not a trained model. It is a Version 1 hourly feature store containing external drivers that can later be joined to real hourly North River influent-flow data.

The main local outputs are:

```text
data/processed/north_river_feature_store_v1.parquet
data/processed/north_river_feature_store_v1.csv
```

These files are generated locally and intentionally not committed to Git.

## Why This Matters

Influent flow is an important operating and planning quantity for wastewater treatment facilities. It affects hydraulic loading, wet-weather capacity, plant operations, and future planning assumptions.

For North River, the problem is not simply “rain now means flow now.” Rainfall can move through the combined sewer system with delays caused by runoff generation, sewer storage, interceptor routing, travel time, antecedent wetness, and possibly tide or water-level conditions near the Hudson River.

That is why this first version focuses on building a time-aligned external-driver dataset before attempting any modeling.

## What Was Built

Version 1 builds a complete hourly dataset from:

```text
2015-01-01 00:00
through
2024-12-31 23:00
```

The feature store includes calendar variables, Central Park rainfall, rainfall history, rolling rainfall features, storm-memory features, Battery water level, tide-history features, tidal phase features, source labels, units, datum, and missing-data flags.

The main build script is:

```text
src/build_feature_store_v1.py
```

The local inspection notebook is:

```text
notebooks/inspect_feature_store_v1.ipynb
```

## Data Sources and Decisions

Central Park rainfall remains the preferred conceptual rainfall assumption because it aligns with the DEP/North River calibration context reviewed for this project. However, the NRCC gauge page, CLIMOD 2, and ACIS checks did not produce a confirmed automated hourly Central Park rainfall export for the full Version 1 period.

For the practical Version 1 build, NOAA LCD Central Park station `USW00094728` was approved as the hourly rainfall fallback. The rainfall loader uses regular hourly `FM-15` observations, buckets the usual `:51` observation time to the hour, treats trace precipitation as `0.0 mm`, and keeps missing rainfall values missing rather than silently filling them.

For tide and water level, I used NOAA CO-OPS Station `8518750`, The Battery. The Battery is a lower Hudson / New York Harbor proxy. It is useful context for North River because of the plant’s location near the Hudson River, but it is not a plant-specific hydraulic boundary condition.

## What The Feature Store Contains

The Version 1 feature store contains:

* a complete hourly timestamp backbone
* hour, day-of-week, month, and weekend features
* cyclical calendar encodings
* hourly rainfall and rainfall lags
* rolling rainfall totals and rolling rainfall maxima
* storm duration, storm total rainfall, and hours since last rain
* 3-day and 7-day antecedent wetness indexes
* Battery water level, water-level lags, changes, and rolling means
* tidal phase sine and cosine features
* rainfall and tide missing-data flags
* rainfall and tide source metadata
* water-level units and datum

## What It Intentionally Excludes

Version 1 intentionally excludes:

* model training
* synthetic North River influent flow
* `influent_flow_mgd`
* target-flow columns
* flow-lag features
* model predictions
* cloud, database, dashboard, Airflow, Docker, or enterprise feature-store tooling

These exclusions are important because the project does not yet have real hourly North River influent-flow target data.

## Validation Summary

The generated feature store passed the current structural validation checks.

| Check                           | Result                |
| ------------------------------- | --------------------- |
| Rows                            | 87,672                |
| Columns                         | 44                    |
| Start timestamp                 | `2015-01-01 00:00:00` |
| End timestamp                   | `2024-12-31 23:00:00` |
| Duplicate timestamps            | 0                     |
| Missing rainfall values         | 1,245                 |
| Missing tide values             | 10                    |
| Forbidden flow / target columns | none                  |

The local inspection notebook also checks the time axis, missing-data flags, rainfall behavior, tide behavior, lag and rolling-feature logic, source metadata, and a Hurricane Ida storm window as a visual sanity check.

## Current Limitations

Central Park rainfall is a point-gauge fallback, not a sewershed-average rainfall product. It is useful for a first version, but it does not fully describe spatial rainfall over the North River drainage area.

The Battery water level is a proxy, not a plant-specific hydraulic boundary condition.

Version 1 uses naive local hourly timestamps. NOAA LCD rainfall is bucketed to the local hour, and NOAA CO-OPS tide data was requested in local station time. Daylight-saving-time handling should be revisited once the target-flow timestamp convention is known.

North River Appendix G is still pending through FOIL. That document may change the hydraulic interpretation, future feature choices, or drainage-area assumptions.

Most importantly, real hourly North River influent-flow data is still missing. Without that target data, this project should not train or claim a forecasting model.

## Next Steps

The next step is to obtain real hourly North River influent-flow data and confirm its timestamp convention.

After that, the project can build a model table by joining the real flow observations to this external-forcing feature store. Only then should target variables, flow lags, train/test splits, baseline models, and forecast-horizon decisions be added.

Useful follow-up checks include:

* compare source timestamps against the target-flow timestamp convention
* revisit daylight-saving-time handling
* review Appendix G when it becomes available
* consider sewershed-average rainfall or spatial rainfall products if North River drainage information becomes available
* start with simple baseline models before trying more complex methods

## Short Version

I built a local Version 1 hourly external-forcing feature store for future North River WRRF influent-flow modeling. It covers 2015 through 2024 at hourly resolution and includes rainfall, tide/water level, calendar, lag, rolling, storm-memory, antecedent wetness, missingness, and source-metadata features. It does not include influent flow, synthetic flow, target columns, model predictions, or model training.

The feature store passed the current structural checks: 87,672 hourly rows, no duplicate timestamps, no missing timestamps, 1,245 missing rainfall values, 10 missing tide values, and no forbidden flow or target columns. The main next step is to obtain real hourly North River influent-flow data so this feature store can be joined to an actual target before any modeling begins.
