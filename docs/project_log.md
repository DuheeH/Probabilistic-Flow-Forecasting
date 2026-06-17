# Project Log

## Project Purpose

- Build a local, lightweight data science project for North River WRRF influent-flow prediction research.
- Immediate goal: create a Version 1 hourly external-forcing feature store.
- Future goal: join real hourly North River influent-flow observations when available and train a baseline forecasting model.

## Current State

- The repository was reset to a cleaner structure.
- Preserved source materials:
  - `data/raw/dep_reports/Monthly_Operating_Efficiency_2025.xlsx`
  - `docs/data_dictionary.md`
  - `docs/source_register.md`
- The immediate build target remains:
  - `data/processed/north_river_feature_store_v1.parquet`
  - `data/processed/north_river_feature_store_v1.csv`

## Advisor Presentation Outline

This outline is intended to become a slide deck for an advisor. It should explain the project as a research process, not just as a coding task.

### 1. Project Motivation

- Influent flow is an important design parameter for wastewater treatment facilities.
  - It affects hydraulic capacity, process loading, wet-weather operation, and planning assumptions.
- North River WRRF influent flow is affected by dry-weather wastewater patterns, wet-weather inflow and infiltration, combined sewer storage, interceptor routing, and tidal or hydraulic boundary conditions.
- A forecasting workflow could eventually help explain and anticipate plant inflow response during wet weather.
- The first step is not model training; it is building a defensible hourly feature dataset.

### 2. Research Question

- Can external hydrologic and tidal forcing features help explain and eventually forecast North River WRRF influent-flow response?
- More specifically, can rainfall history, rainfall intensity, antecedent wetness, calendar effects, and tidal water level provide useful predictors once real hourly influent-flow data is available?

### 3. Why North River WRRF Is Being Studied

- North River WRRF is being studied because I work on a North River project.
- North River WRRF serves a dense, hydraulically complex Manhattan drainage area.
- The facility is relevant to NYC combined sewer overflow and long-term control planning work.
- North River is adjacent to the Hudson River, making tidal and downstream boundary conditions worth considering.
- DEP reports provide enough methodology context to start a Version 1 feature-store build even before plant-specific Appendix G material is available.

### 4. Why This Is Not A Generic Weather-Prediction Problem

- The target system is a storage-dominated combined sewer and interceptor system, not a direct weather sensor.
- Rainfall does not translate instantly into influent flow.
- Important physical processes include:
  - runoff generation
  - surface and sewer travel time
  - in-system storage
  - interceptor routing
  - delayed infiltration / inflow
  - possible tidal or downstream hydraulic influence
- Therefore, the feature dataframe must include lag, accumulation, intensity, antecedent wetness, and tide context.

### 5. DEP Report Review Performed

- Reviewed NYC DEP InfoWorks Citywide Recalibration Report.
  - Used for calibration methodology and rainfall gauge assignment context.
- Reviewed NYC DEP Hydraulic Capacity Analysis Report, 2012.
  - Used for hydraulic capacity, storage, interceptor, and wet-weather context.
- Identified that North River Appendix G would be highly useful but is not currently available.
- Preserved a monthly operating efficiency workbook as DEP-style monthly plant context.

### 6. Key Findings From DEP Reports

- NYC DEP InfoWorks Citywide Recalibration Report:
  - DEP modeling work supports treating rainfall gauge choice as a methodological decision, not a casual weather-data choice.
  - North River calibration context points toward Central Park / CPK rainfall for Version 1.
  - Rainfall inputs should be tied to the drainage / model calibration context rather than selected only by convenience.
- NYC DEP Hydraulic Capacity Analysis Report, 2012:
  - Travel time and storage matter in the sewer system.
  - Wet-weather response can be substantially different from dry-weather flow.
  - Hydraulic capacity and interceptor behavior support using lagged and accumulated hydrologic forcing features.
- North River Appendix G:
  - Not currently available.
  - Expected to be important for North River-specific drainage area, sewershed geometry, regulators, interceptors, or hydraulic constraints.
  - Has been requested via FOIL.
- Monthly Operating Efficiency workbook:
  - Provides monthly plant operating context, including North River monthly flow summaries.
  - It is not hourly influent-flow target data and should not be used as the hourly ML target.
- Overall takeaway:
  - A plant-specific drainage boundary would improve future rainfall feature engineering.

### 7. Why Central Park Rainfall Is Used In Version 1

- Central Park rainfall is consistent with the DEP North River calibration approach identified during report review.
- It is a defensible point-gauge assumption while North River-specific sewershed geometry is unavailable.
- Version 1 should document this as an assumption, not as a claim that Central Park perfectly represents all rainfall over the drainage area.

### 8. Why Tide Level Is Considered

- North River is adjacent to the Hudson River.
- Tidal conditions may affect hydraulic gradients, outfalls, regulators, or downstream boundary behavior.
- Tide features are included to test whether water-level state or tidal phase helps explain future influent-flow response.
- Tide is treated as an external forcing / context variable, not as proof of a specific hydraulic mechanism.

### 9. Why The Battery Is Used As A Tide Proxy

- NOAA CO-OPS Station 8518750, The Battery, is an official long-running water-level station for New York Harbor / lower Hudson conditions.
- It is the preferred Version 1 tide source among the candidate stations reviewed.
- It is only a proxy.
  - It is not a plant-specific hydraulic boundary.
  - The project must document water-level units, datum, source, and timestamp handling.

### 10. Data Sources Considered

- Cornell NRCC NYC Weather Network / Central Park gauge.
- NOAA CO-OPS Station 8518750, The Battery.
- NOAA Local Climatological Data.
- MRMS precipitation.
- ERA5-Land.
- USGS Water Data API.
- NYC DEP wastewater performance data.
- NYC DEP InfoWorks Citywide Recalibration Report.
- NYC DEP Hydraulic Capacity Analysis Report.
- North River Appendix G, pending / unavailable.
- George Washington Bridge public tide forecast, reference only.

### 11. Data Sources Selected

- Version 1 rainfall:
  - Cornell NRCC Central Park gauge.
- Version 1 tide / water level:
  - NOAA CO-OPS Station 8518750, The Battery.
- Optional Version 1 temperature:
  - NOAA Local Climatological Data, only if easy and non-blocking.
- Methodology context:
  - DEP InfoWorks Citywide Recalibration Report.
  - DEP Hydraulic Capacity Analysis Report.

### 12. Data Sources Deferred

- MRMS:
  - Deferred until North River sewershed geometry or Appendix G is available.
- ERA5-Land:
  - Deferred as a future comparison or hydrologic-state supplement.
- USGS Water Data API:
  - Deferred unless directly relevant Hudson River, groundwater, or hydrologic stations are identified.
- NYC DEP public wastewater performance data:
  - Useful for context, but not assumed to be hourly target data.
- Tide forecast websites:
  - Reference only, not a reproducible data source.

### 13. Technology Used

- Python for scripting and data processing.
- Polars for dataframe operations.
- Parquet as the primary storage format.
- CSV as a secondary inspection/debug export.
- NumPy for mathematical feature transforms.
- Matplotlib for future plots and quality checks.
- Requests for lightweight source downloads.
- Jupyter only if exploratory notebooks become useful later.

### 14. What Parquet Is

- Parquet is a columnar file format for tabular data.
- It stores data efficiently and preserves column types better than CSV.
- It is appropriate for the main processed feature-store output.
- CSV is still exported for human inspection and easy debugging.

### 15. Why Polars Was Selected

- Polars is a fast dataframe library with strong support for typed columns, joins, rolling operations, and Parquet.
- It is well suited for building an hourly feature dataframe.
- It keeps the project lightweight without requiring databases or distributed systems.
- Pandas can be used later only as a fallback if a specific data source is awkward in Polars.

### 16. What The Feature Dataframe Contains

- A complete hourly timestamp backbone.
- Calendar features:
  - hour of day
  - day of week
  - month
  - weekend flag
  - cyclic encodings
- Rainfall features:
  - current rainfall
  - rainfall lags
  - rolling rainfall accumulations
  - rainfall intensity features
  - antecedent wetness features
  - missing-data flags
- Tide / water-level features:
  - observed water level
  - water-level lags
  - water-level changes
  - rolling water-level summaries
  - tidal phase sine/cosine features
  - missing-data flags
- Source metadata:
  - rainfall source
  - tide source
  - water-level units
  - water-level datum
  - timezone assumptions

### 17. Assumptions Made

- Central Park rainfall is an acceptable Version 1 point-gauge rainfall assumption.
- The Battery is an acceptable Version 1 tide proxy.
- The hourly backbone defines the time axis; source data joins onto it.
- Missing rainfall should not automatically be interpreted as zero unless a no-rain observation is confirmed.
- Calendar features should be generated using a documented local-time convention.
- Temperature is useful but optional and should not block Version 1.

### 18. Limitations

- No real hourly North River influent-flow target data yet.
- No North River-specific sewershed boundary yet.
- North River Appendix G is unavailable.
- The Battery is not a plant-specific hydraulic boundary condition.
- Central Park rainfall does not capture spatial rainfall variation across the drainage area.
- Monthly operating efficiency data is not suitable as the hourly model target.

### 19. What Was Intentionally Excluded From Version 1

- Machine-learning model training.
- Synthetic North River influent flow.
- Target-flow columns.
- Flow lag features.
- Cloud infrastructure.
- Docker.
- Databases.
- Airflow.
- Dashboards.
- Enterprise feature-store tools.

### 20. What Will Change When Appendix G Becomes Available

- North River Appendix G has been requested via FOIL.
- The project may gain North River-specific sewershed geometry, subcatchments, interceptors, regulators, or hydraulic constraints.
- Rainfall strategy may change from Central Park point rainfall to sewershed-weighted rainfall.
- MRMS or other spatial rainfall products may become more useful.
- Feature engineering may become more physically specific to North River routing and storage.
- Advisor presentation can better connect features to plant-specific hydraulic structure.

### 21. What Will Change When Hourly Influent Data Becomes Available

- A new model table can be created by joining:
  - `north_river_feature_store_v1`
  - actual hourly `influent_flow_mgd`
  - causal flow lag features
- The project can move from feature-store construction to supervised learning.
- Flow lag and rolling flow features can be added, but only using real observed flow.
- Model evaluation can begin with time-aware train/validation splits.

### 22. Next Steps Toward ML Modeling

- Finish the Version 1 external-forcing feature store.
- Validate timestamp continuity, missingness, units, and source coverage.
- Obtain real hourly North River influent-flow data.
- Build `north_river_model_table_v1`.
- Train simple baseline models first.
  - Linear / regularized baseline if useful.
  - Random Forest.
  - XGBoost or LightGBM.
- Compare models using time-aware validation.
- Use feature importance and error analysis to explain hydrologic response patterns.

## Implementation Notes

### Timestamp and Time Zone Assumptions

- To be finalized during implementation.
- Preferred approach:
  - Build a complete hourly timestamp backbone first.
  - Store timestamps consistently.
  - Use America/New_York local time for calendar features.
  - Document source timestamp conventions for rainfall and NOAA tide data.
  - Track duplicated or missing local hours caused by daylight saving time transitions.

### NRCC / CLIMOD 2 Rainfall Acquisition Checkpoint

- CLIMOD 2 URL checked:
  - `http://climod2.nrcc.cornell.edu/`
- Central Park station status:
  - Found through the CLIMOD / ACIS station metadata path.
  - Station name returned: `NY CITY CENTRAL PARK`.
  - Relevant identifiers returned:
    - `KNYC 5`
    - `USW00094728 6`
    - `USW00094728 32`
    - `NYC 3`
    - `305801 2`
  - Unified ACIS id returned: `18345`.
- Hourly precipitation status:
  - Central Park precipitation exists for the requested broad period.
  - The direct CLIMOD 2 product menu inspected did not expose a clear hourly data product.
  - The tested ACIS `StnData` request with `pcpn` returned daily precipitation, not hourly precipitation.
  - Attempts to request hourly precipitation using `hly_pcpn` or hourly interval-style element objects returned `bad args`.
- Export status:
  - CLIMOD 2 exposes CSV options for daily/monthly products.
  - A confirmed hourly precipitation CSV export was not found during this checkpoint.
- Automation status:
  - Automated station metadata lookup is possible through the CLIMOD / ACIS service path.
  - Automated hourly precipitation acquisition is not yet confirmed.
- Timestamp convention found or assumed:
  - No hourly CLIMOD 2 export was obtained, so hourly timestamp convention remains unresolved.
  - Manual download, if found, must be inspected before assuming UTC or America/New_York.
- Units found or assumed:
  - ACIS documentation identifies `pcpn` as precipitation in inches.
  - No CLIMOD 2 hourly export was obtained, so the project should not silently assume units for a manual file unless the file or export page clearly identifies them.
- Expected rainfall file path if a CLIMOD 2 hourly export is obtained manually:
  - `data/raw/weather/central_park_nrcc_climod2_hourly_rainfall_2015_2024.csv`
- Loader status:
  - `src/rainfall_loader.py` expects the manual CLIMOD 2 rainfall file at the path above.
  - It standardizes rainfall to:
    - `timestamp`
    - `rain_mm`
  - It refuses to guess units when units are unclear.
- Limitation:
  - CLIMOD 2 appears usable for Central Park station discovery and daily precipitation exports.
  - CLIMOD 2 has not yet been confirmed usable for the required hourly precipitation amount export.

### ACIS / NOAA Regional Climate Centers Investigation

- Reason for checking ACIS:
  - CLIMOD 2 is connected to the NOAA Regional Climate Centers / ACIS service ecosystem.
  - After the CLIMOD 2 web path did not clearly expose an hourly Central Park rainfall export, ACIS was checked directly as the next source in the same family.
- ACIS URL checked:
  - `https://data.rcc-acis.org`
- Central Park station status:
  - Central Park was confirmed through ACIS metadata.
  - Station name returned: `NY CITY CENTRAL PARK`.
  - Relevant identifiers returned:
    - `KNYC 5`
    - `USW00094728 6`
    - `USW00094728 32`
    - `NYC 3`
    - `305801 2`
  - Unified ACIS id returned: `18345`.
- Daily precipitation status:
  - ACIS `StnData` calls using `pcpn` returned daily Central Park precipitation values.
  - This confirms precipitation availability, but not the hourly rainfall product required for the Version 1 feature store.
- Hourly precipitation status:
  - Attempts to request hourly precipitation using candidate hourly element names and interval-style element objects were not accepted.
  - Tested hourly-style requests returned `bad args`.
  - A separate `HourlyData` endpoint was not found.
- Conclusion:
  - ACIS confirms the Central Park station and daily precipitation.
  - ACIS did not confirm a downloadable hourly Central Park precipitation amount suitable for this project.
  - ACIS should not be used as the Version 1 hourly rainfall source unless an official hourly precipitation endpoint or export format is later identified.

### NOAA LCD Fallback Investigation

- Reason for checking NOAA LCD:
  - The preferred NRCC / CLIMOD 2 path did not produce a confirmed hourly rainfall export.
  - ACIS confirmed Central Park metadata and daily precipitation, but not hourly precipitation.
  - NOAA Local Climatological Data was already listed as a possible fallback because it contains station-based hourly weather observations.
- NOAA LCD product page checked:
  - `https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data`
- Central Park station status:
  - NOAA LCD bulk files were found for Central Park station `USW00094728`.
  - The 2020 sample file identifies the station as `NY CITY CENTRAL PARK, NY US`.
- Hourly precipitation status:
  - The LCD product documentation describes hourly observations and hourly precipitation sections.
  - The Central Park yearly CSV sample includes:
    - `DATE`
    - `STATION`
    - `NAME`
    - `REPORT_TYPE`
    - `HourlyPrecipitation`
  - Sample hourly rows use timestamps such as `2020-01-01T00:51:00`, which means the raw observations are not exactly on the top of the hour and will need explicit hourly standardization during feature-store construction.
- Export status:
  - NCEI object storage exposes yearly Central Park CSV files using a stable pattern:
    - `https://www.ncei.noaa.gov/oa/local-climatological-data/v2/access/{year}/LCD_USW00094728_{year}.csv`
  - Files were confirmed for at least 2015, 2020, and 2024.
  - This supports building a local combined 2015-2024 fallback file.
- Automation status:
  - Automated download appears straightforward using the yearly CSV URL pattern.
  - A local downloader has been added at `src/download_noaa_lcd.py`.
- Units found or assumed:
  - NOAA LCD documentation states that LCDv2 bulk CSV files are provided in SI / metric units.
  - The rainfall loader treats NOAA LCD `HourlyPrecipitation` as millimeters.
- Expected fallback rainfall file path:
  - `data/raw/weather/central_park_noaa_lcd_hourly_weather_2015_2024.csv`
- Limitations:
  - NOAA LCD is not the original preferred NRCC / Cornell source.
  - NOAA LCD should be used as an explicit fallback, not as an undocumented silent source switch.
  - Timestamp convention and hourly aggregation rules must be documented during the feature-store build.

### Rainfall Source Decision Status

- Preferred rainfall source:
  - NRCC / Cornell Central Park hourly rainfall, if a valid hourly export can be obtained.
- Current preferred-source status:
  - CLIMOD 2 / NRCC has not yet produced a confirmed hourly export.
  - ACIS confirms Central Park and daily precipitation, but not hourly precipitation.
- Explicit fallback:
  - NOAA/NCEI LCD Central Park station `USW00094728`.
  - This fallback is now approved for Version 1 Central Park hourly precipitation.
- Current build status:
  - The NOAA LCD fallback file has been downloaded locally.
  - The final feature store has not been built yet.
  - It should remain blocked until tide data is acquired and the final hourly backbone join is implemented/validated.

### NOAA LCD Download And Rainfall Validation

- Downloaded local fallback file:
  - `data/raw/weather/central_park_noaa_lcd_hourly_weather_2015_2024.csv`
- Source file details:
  - Station identifier: `USW00094728`
  - Station name: `NY CITY CENTRAL PARK, NY US`
  - Raw row count: 116,737
  - Raw timestamp range: `2015-01-01T00:00:00` through `2024-12-31T23:59:00`
  - Raw reports include `FM-15`, `FM-16`, daily summary, and monthly summary records.
- Loader interpretation:
  - Use regular hourly `FM-15` observation rows only.
  - Convert raw observation timestamps such as `2015-01-01T00:51:00` to the corresponding hour bucket, e.g. `2015-01-01 00:00:00`.
  - Do not sum duplicate intra-hour reports because special `FM-16` rows can contain conflicting partial-period precipitation values.
  - NOAA LCD `HourlyPrecipitation` is treated as millimeters because LCDv2 bulk CSV files are documented as SI / metric.
  - Trace precipitation values (`T`) are treated as `0.0 mm` for Version 1 and documented as trace handling, not as missing rainfall.
  - Blank or invalid precipitation values remain missing and set `rain_missing_flag = 1`.
- Standardized loader output:
  - Columns: `timestamp`, `rain_mm`, `rain_missing_flag`, `rain_source`
  - Standardized row count: 87,541
  - Standardized timestamp range: `2015-01-01 00:00:00` through `2024-12-31 23:00:00`
  - Duplicate standardized timestamps: 0
  - Missing standardized precipitation values: 1,114
  - Expected local-hour count for 2015-01-01 00:00 through 2024-12-31 23:00: 87,672
  - Missing expected hour buckets in NOAA LCD FM-15 observations: 131
- Timestamp / timezone assumption:
  - NOAA LCD timestamps are treated as local station observation timestamps for Central Park.
  - Version 1 calendar features should use the local timestamp convention and document daylight-saving-time gaps or repeated hours.
- Limitation:
  - The rainfall input is usable for Version 1, but it is not a perfect complete hourly time axis.
  - The final feature-store build must create its own complete hourly backbone and left-join rainfall onto it, preserving missing rainfall flags.

### Guardrails

- Do not train a model yet.
- Do not create synthetic influent flow.
- Do not create target-flow columns in the Version 1 feature store.
- Do not add cloud, Docker, databases, Airflow, dashboards, or enterprise feature-store tools.
