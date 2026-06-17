# Methodology Outline

These are presentation-style notes for explaining the project. The goal is to show the research logic, not just the code.

## 1. Motivation

- Influent flow is an important design parameter for wastewater treatment facilities.
- For North River WRRF, flow can reflect rainfall, sewer storage, routing delays, dry-weather patterns, and possible tidal effects.
- I started with external features because I do not have real hourly North River influent-flow data yet.

## 2. Research Question

- Can rainfall history, tide level, calendar timing, and antecedent wetness help explain future North River influent-flow response?
- Once real hourly influent data is available, can these features support a first forecasting model?

## 3. Why North River

- I am focusing on North River because my project work is tied to North River.
- It is a hydraulically complex Manhattan WRRF near the Hudson River.
- DEP reports give enough context to start a careful Version 1 feature build.

## 4. Why External Features First

- A model needs a real target. I do not have hourly North River influent-flow data yet.
- Creating fake flow would make the project misleading.
- Building the external-forcing feature store first lets the project move forward without inventing a target.

## 5. Rainfall Source Decision

- Central Park rainfall is the preferred conceptual assumption because it aligns with DEP/North River calibration context.
- I checked NRCC, CLIMOD 2, and ACIS first.
- Those paths did not provide a confirmed automated hourly Central Park precipitation export.
- NOAA LCD Central Park station `USW00094728` is used as the practical fallback for V1.

## 6. Tide Source Decision

- NOAA CO-OPS Station `8518750`, The Battery, is used for Version 1 water level.
- The Battery is a tide proxy, not a plant-specific hydraulic boundary condition.
- V1 uses hourly height, metric units, datum `MLLW`, and local station time.

## 7. What V1 Contains

- Complete hourly backbone from `2015-01-01 00:00` through `2024-12-31 23:00`.
- Calendar features.
- Rainfall, rainfall lags, rolling rainfall, storm features, and antecedent wetness.
- Tide level, tide lags, water-level changes, rolling means, and tidal phase features.
- Source labels, units, datum, and missing-data flags.

## 8. Validation Result

- Rows: 87,672.
- Duplicate timestamps: 0.
- Missing timestamps: 0.
- Missing rainfall values: 1,245.
- Missing tide values: 10.
- Forbidden flow/target columns: none.

## 9. Limitations

- Central Park rainfall is a point-gauge fallback, not sewershed-average rainfall.
- The Battery is not a plant-specific boundary condition.
- V1 uses naive local timestamps; daylight-saving-time handling is a known limitation.
- North River Appendix G is still pending.
- Real hourly North River influent-flow data is still needed.

## 10. Next Step

- Obtain real hourly North River influent-flow data.
- Confirm its timestamp convention.
- Build `north_river_model_table_v1`.
- Train baseline models only after the real target data is available.
