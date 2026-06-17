# Advisor Methodology Outline

## 1. Motivation

- Influent flow is an important design parameter for wastewater treatment facilities.
- North River WRRF influent flow is affected by rainfall response, sewer storage, routing, and possible tidal boundary conditions.
- The first deliverable is a defensible hourly external-forcing feature store, not a trained model.

## 2. Research Question

- Can external hydrologic and tidal forcing features help explain and eventually forecast North River WRRF influent-flow response once real hourly influent data is available?

## 3. Study Site

- North River WRRF is the focus because the project is tied to North River work.
- The site is hydraulically complex and adjacent to the Hudson River.
- DEP methodology reports support careful treatment of rainfall source choice and hydraulic context.

## 4. Source Review

- DEP InfoWorks Citywide Recalibration Report:
  - Supports the Central Park rainfall assumption as a methodology-driven starting point.
- DEP Hydraulic Capacity Analysis Report:
  - Supports lagged rainfall, rolling rainfall, and storage/routing feature logic.
- North River Appendix G:
  - Requested via FOIL and expected to improve future North River-specific interpretation.

## 5. Version 1 Data Decisions

- Rainfall:
  - NRCC / Central Park remains the preferred conceptual source.
  - NRCC gauge, CLIMOD 2, and ACIS were investigated first.
  - NOAA LCD Central Park `USW00094728` is approved as the practical fallback.
- Tide:
  - NOAA CO-OPS Station 8518750, The Battery, is used as the Version 1 tide proxy.
  - Version 1 uses hourly height, metric units, datum `MLLW`, local station time.

## 6. Feature Store Built

- Outputs:
  - `data/processed/north_river_feature_store_v1.parquet`
  - `data/processed/north_river_feature_store_v1.csv`
- Time range:
  - `2015-01-01 00:00` through `2024-12-31 23:00`
- Rows:
  - 87,672 complete hourly records
- Contents:
  - calendar features
  - rainfall lags and rolling rainfall
  - storm and antecedent wetness features
  - tide lags, changes, rolling means, and tidal harmonic features
  - source labels, units, datum, and missing-data flags

## 7. Version 1 Exclusions

- No model training.
- No synthetic influent flow.
- No `influent_flow_mgd`.
- No flow-lag features.
- No target-flow columns.

## 8. Limitations

- Central Park rainfall is a point-gauge fallback, not sewershed-average rainfall.
- The Battery is a tide proxy, not a plant-specific hydraulic boundary.
- Hourly North River influent-flow data is not available yet.
- Appendix G is not available yet.

## 9. Next Step

- Obtain real hourly North River influent-flow data.
- Build `north_river_model_table_v1` by joining real target flow to the external-forcing feature store.
- Train baseline ML models only after real target data is available.
