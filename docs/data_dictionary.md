# Data Dictionary

This document defines the intended schema for `data/processed/north_river_feature_store_v1.parquet` and `data/processed/north_river_feature_store_v1.csv`.

Version 1 is an external-forcing feature store only. It must not include target-flow columns, synthetic influent flow, model predictions, or flow lag features.

## North River Feature Store V1 Schema

| Column | Data Type | Units / Range | Tier | Build Status | Description | Critical Rules / Notes |
| --- | --- | --- | --- | --- | --- | --- |
| timestamp | datetime | hourly | 1 | V1 required | Master hourly timestamp backbone | Must be complete hourly index. Do not let rainfall or tide source define the time axis. For NOAA LCD rainfall, use local Central Park observation time bucketed to the hour. |
| hour_of_day | int8 | 0–23 | 1 | V1 required | Hour extracted from timestamp | Used for diurnal wastewater patterns. |
| day_of_week | int8 | 0–6 | 1 | V1 required | Weekday index | Define mapping explicitly. Recommended: Monday = 0. |
| month | int8 | 1–12 | 1 | V1 required | Calendar month | Captures seasonal effects. |
| is_weekend | bool / int8 | 0/1 | 1 | V1 required | Weekend indicator | Derived from day_of_week. |
| hour_sin | float32 | -1 to 1 | 1 | V1 required | Cyclical hour encoding | Use with hour_cos. Prevents hour 23 and 0 from being treated as far apart. |
| hour_cos | float32 | -1 to 1 | 1 | V1 required | Cyclical hour encoding | Use with hour_sin. |
| dow_sin | float32 | -1 to 1 | 1 | V1 required | Cyclical weekday encoding | Use with dow_cos. |
| dow_cos | float32 | -1 to 1 | 1 | V1 required | Cyclical weekday encoding | Use with dow_sin. |
| month_sin | float32 | -1 to 1 | 1 | V1 required | Cyclical annual encoding | Captures smooth seasonal periodicity. |
| month_cos | float32 | -1 to 1 | 1 | V1 required | Cyclical annual encoding | Use with month_sin. |
| rain_mm | float32 | mm/hr accumulation | 1 | V1 required | Hourly rainfall accumulation | NOAA LCD fallback uses `HourlyPrecipitation` from `FM-15` rows, treated as millimeters. Do not assume NaN = 0. Trace `T` is treated as 0.0 mm and documented. |
| rain_t | float32 | mm/hr accumulation | 1 | V1 required | Current-hour rainfall feature | Usually equal to rain_mm. Included for schema readability. |
| water_level | float32 | meters | 1 | Built in V1 | NOAA CO-OPS hourly height from The Battery | Version 1 uses Station 8518750, hourly height, metric units, datum `MLLW`, local station time. |
| temperature_c | float32 | °C | 3 | V1 optional | Ambient air temperature | Useful for seasonality, snowmelt, and infiltration context. Do not block V1 if unavailable. |
| rain_t_1 | float32 | mm/hr | 1 | V1 required | Rainfall 1 hour ago | Use shift(1). Causal only. |
| rain_t_3 | float32 | mm/hr | 2 | V1 should-have | Rainfall 3 hours ago | Captures short routing delays. |
| rain_t_6 | float32 | mm/hr | 1 | V1 required | Rainfall 6 hours ago | Captures delayed sewer response and storage effects. |
| rain_t_12 | float32 | mm/hr | 2 | V1 should-have | Rainfall 12 hours ago | Useful for longer recession / delayed response. |
| rain_t_24 | float32 | mm/hr | 1 | V1 required | Rainfall 24 hours ago | Captures daily-scale wetness and delayed effects. |
| rain_last_6h | float32 | mm | 2 | V1 should-have | Rolling 6-hour rainfall sum | Use shift(1) before rolling if features are meant for forecasting. |
| rain_last_12h | float32 | mm | 2 | V1 should-have | Rolling 12-hour rainfall sum | Use shifted rolling sum. |
| rain_last_24h | float32 | mm | 1 | V1 required | Rolling 24-hour rainfall sum | High-value hydrologic memory feature. Use shift(1) before rolling. |
| rain_last_72h | float32 | mm | 2 | V1 should-have | Rolling 72-hour rainfall sum | Represents multi-day antecedent wetness. |
| rain_max_last_6h | float32 | mm/hr | 2 | V1 should-have | Maximum hourly rainfall in prior 6 hours | Use shifted rolling max. Captures peak intensity. |
| rain_max_last_24h | float32 | mm/hr | 2 | V1 should-have | Maximum hourly rainfall in prior 24 hours | Distinguishes intense storms from long low-intensity events. |
| storm_duration | int16 | hours | 2 | V1 should-have | Consecutive wet hours in current storm | Event-based logic. If not raining, value should be 0. Define wet threshold, e.g. rain_mm > 0.1 mm. |
| storm_total_rainfall | float32 | mm | 2 | V1 should-have | Cumulative rainfall during current storm | Resets on dry hour. Do not use naive cumulative sum across dry periods. |
| hours_since_last_rain | int16 | hours | 2 | V1 should-have | Hours since rainfall last exceeded threshold | Must reset correctly when rainfall exceeds threshold. |
| AWI_3d | float32 | mm-like index | 2 | V1 should-have | 3-day antecedent wetness index | Use exponentially weighted rainfall, approximately 72-hour span. |
| AWI_7d | float32 | mm-like index | 2 | V1 should-have | 7-day antecedent wetness index | Use exponentially weighted rainfall, approximately 168-hour span. |
| water_level_t_1 | float32 | same as water_level | 1 | V1 required | Water level 1 hour ago | Use shift(1). |
| water_level_t_6 | float32 | same as water_level | 2 | V1 should-have | Water level 6 hours ago | Useful because semi-diurnal tides have roughly 6-hour rise/fall phases. |
| water_level_change_1h | float32 | water-level units/hr | 1 | V1 required | 1-hour water-level change | Current water level minus water level 1 hour ago. |
| water_level_change_3h | float32 | water-level units/3hr | 2 | V1 should-have | 3-hour water-level change | Captures sustained rising/falling tide conditions. |
| water_level_rolling_mean_6h | float32 | same as water_level | 2 | V1 should-have | Prior 6-hour mean water level | Use shift(1) before rolling for forecasting-safe features. |
| water_level_rolling_mean_24h | float32 | same as water_level | 2 | V1 should-have | Prior 24-hour mean water level | Captures persistent tidal / water-level loading. |
| tidal_phase_sin | float32 | -1 to 1 | 2 | V1 should-have | Synthetic semi-diurnal tidal phase | Use elapsed hours from fixed timestamp, not row index unless hourly backbone is validated complete. |
| tidal_phase_cos | float32 | -1 to 1 | 2 | V1 should-have | Synthetic semi-diurnal tidal phase | Use with tidal_phase_sin. Period ≈ 12.42 hours. This does not replace observed water_level. |
| rain_missing_flag | int8 | 0/1 | 1 | V1 required | Rainfall missingness indicator | 1 means missing or invalid rainfall. Do not silently fill missing rainfall. Trace precipitation is not treated as missing in Version 1. |
| tide_missing_flag | int8 | 0/1 | 1 | Built in V1 | Tide missingness indicator | 1 means missing after joining NOAA CO-OPS hourly height to the complete backbone. Missing tide is not filled. |
| temperature_missing_flag | int8 | 0/1 | 3 | V1 optional | Temperature missingness indicator | Only needed if temperature_c is included. |
| rain_source | string | source label | 1 | V1 required | Rainfall provenance | Version 1 fallback label: `NOAA NCEI LCD Central Park USW00094728 fallback`. NRCC / Central Park remains the preferred conceptual source. |
| tide_source | string | source label | 1 | Built in V1 | Tide provenance | Version 1 label: `NOAA CO-OPS 8518750 The Battery`. |
| water_level_units | string | metric | 1 | Built in V1 | Water-level units | NOAA CO-OPS request used `units=metric`. |
| water_level_datum | string | MLLW | 1 | Built in V1 | Vertical datum | NOAA CO-OPS request used `datum=MLLW`. |
| timezone_assumption | string | local station time | 1 | V1 metadata | Timestamp convention note | Could be stored as metadata rather than repeated per row. V1 uses a naive local hourly backbone; NOAA LCD rainfall is bucketed to local Central Park hour; NOAA CO-OPS tide is requested with `time_zone=lst_ldt`. |
| influent_flow_mgd | float32 | MGD | Future | V2 model table only | Actual North River influent flow target | Do not build tonight unless real hourly influent flow data exists. Target variable. |
| flow_t_1 | float32 | MGD | Future | V2 model table only | Flow 1 hour ago | Requires real influent_flow_mgd. Autoregressive feature. |
| flow_t_3 | float32 | MGD | Future | V2 model table only | Flow 3 hours ago | Requires real influent_flow_mgd. |
| flow_t_6 | float32 | MGD | Future | V2 model table only | Flow 6 hours ago | Requires real influent_flow_mgd. |
| flow_t_12 | float32 | MGD | Future | V2 model table only | Flow 12 hours ago | Requires real influent_flow_mgd. |
| flow_t_24 | float32 | MGD | Future | V2 model table only | Flow 24 hours ago | Captures daily persistence. Requires real influent data. |
| flow_mean_6h | float32 | MGD | Future | V2 model table only | Prior 6-hour mean flow | Use shift(1) before rolling. Requires real influent data. |
| flow_mean_24h | float32 | MGD | Future | V2 model table only | Prior 24-hour mean flow | Use shift(1) before rolling. Requires real influent data. |
| flow_std_24h | float32 | MGD | Future | V2 model table only | Prior 24-hour flow variability | Use shift(1) before rolling. Requires real influent data. |
| is_holiday | bool / int8 | 0/1 | 3 | Future optional | Holiday indicator | Useful later for human wastewater generation patterns. Not necessary for tonight. |
| Critical Implementation Rules |  |  |  |  |  |  |
| The hourly backbone defines the time axis. Rainfall and tide data must join onto it. |  |  |  |  |  |  |
| Confirmed no-rain hours may be represented as 0. Unknown rainfall hours should be missing or imputed with rain_missing_flag = 1. |  |  |  |  |  |  |
| Rolling rainfall and rolling tide features should use shifted inputs when designing for forecasting. |  |  |  |  |  |  |
| Storm features must be event-based. Dry periods should not accumulate storm duration or storm rainfall. |  |  |  |  |  |  |
| Tidal harmonic features should be based on elapsed time, not row number, unless the hourly backbone is already verified complete. |  |  |  |  |  |  |
| Keep Version 1 external forcing features separate from Version 2 model-target features. |  |  |  |  |  |  |
| NOAA LCD fallback rainfall should use regular hourly `FM-15` rows only. Special `FM-16` rows should not be summed into hourly totals. |  |  |  |  |  |  |
| NOAA CO-OPS Version 1 tide should use Station 8518750 The Battery, hourly height, metric units, datum MLLW, and local station time. |  |  |  |  |  |  |
| The Version 1 deliverable is: |  |  |  |  |  |  |
| north_river_feature_store_v1.parquet |  |  |  |  |  |  |
| north_river_feature_store_v1.csv |  |  |  |  |  |  |
| The future model table should be created only after real hourly influent data is obtained: |  |  |  |  |  |  |
| north_river_model_table_v1 |  |  |  |  |  |  |

## Explicitly Excluded From Version 1

- 
- Flow lag features
- Synthetic target values
- Model predictions

Those belong in a future model table only after real hourly North River influent-flow observations are available.
