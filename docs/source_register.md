# Source Register

This document records methodology, data, and reference sources for the North River WRRF feature-store project. Sources are organized in the order they were explored or are expected to support the research workflow.

## A. Methodology And Project Justification Sources

| Source | URL | Project Role | Status | Variables / Information Of Interest | Reason For Inclusion | Limitations | Approved For Version 1 Production Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NYC DEP InfoWorks Citywide Recalibration Report | https://www.nyc.gov/assets/dep/downloads/pdf/water/nyc-waterways/citywide-ltcp/infoworks-citywide-recalibration-report.pdf | Methodology / model calibration context | Reviewed | Rainfall gauge assignment logic, calibration methodology, model assumptions | Supports the Central Park rainfall assumption and explains why rainfall source choice is methodological | Report, not time-series data | Yes, as methodology support |
| NYC DEP Hydraulic Capacity Analysis Report, 2012 | https://www.nyc.gov/assets/dep/downloads/pdf/water/nyc-waterways/citywide-ltcp/hydraulic-capacity-analysis-report-2012.pdf | Hydraulic context | Reviewed | Hydraulic capacity, storage, interceptor behavior, wet-weather response context | Supports lagged rainfall, rolling rainfall, storage, and routing feature logic | North River Appendix G is not currently available | Yes, as methodology support |
| Appendix G - North River, Hydraulic Capacity Analysis | FOIL request pending | Future North River-specific hydraulic / geometry context | Requested via FOIL | Potential sewershed boundary, subcatchments, regulators, interceptors, hydraulic constraints | Could improve physical interpretation and future spatial rainfall features | Not currently available | No, deferred until received |
| Monthly Operating Efficiency workbook | `data/raw/dep_reports/Monthly_Operating_Efficiency_2025.xlsx` | Monthly plant context | Preserved as raw context | Monthly plant flow and performance summaries | Useful context for advisor discussion and monthly-scale sanity checks | Not hourly target data; not suitable for model training target | No, context only |

## B. Rainfall Source Exploration Sequence

| Source | URL | Project Role | Status | Variables / Information Of Interest | Reason For Inclusion | Limitations | Approved For Version 1 Production Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NRCC NYC Weather Network / Central Park gauge | https://www.nrcc.cornell.edu/wxstation/gauges/gauges.html#nycthr | Preferred Version 1 rainfall concept | Preferred but blocked / manual UI uncertain | Central Park hourly rainfall accumulation | Most consistent with DEP / North River calibration logic | JavaScript gauge interface; automated export not confirmed | Not yet |
| CLIMOD 2 | http://climod2.nrcc.cornell.edu/ | NRCC/Cornell source path investigation | Investigated | Central Park precipitation; station metadata | Possible Cornell/NRCC path for Central Park rainfall | Central Park metadata found, but hourly precipitation export not confirmed | Not yet |
| ACIS / NOAA Regional Climate Centers | https://data.rcc-acis.org | RCC/ACIS station metadata and precipitation investigation | Investigated; not usable for hourly rainfall based on tested calls | `pcpn`, Central Park metadata, station identifiers | CLIMOD 2 is built on ACIS/RCC services, so this was the next direct path to test | Central Park confirmed, but `pcpn` returned daily values; hourly element attempts returned `bad args`; no hourly endpoint confirmed | No, for hourly rainfall |
| NOAA/NCEI Local Climatological Data | https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data | Explicit Central Park hourly precipitation fallback | Usable fallback confirmed | `DATE`, `HourlyPrecipitation`, station id/name, hourly weather fields | LCDv2 contains hourly observations and hourly precipitation; Central Park yearly CSV files exist in NCEI object storage | Fallback, not original preferred NRCC source; timestamp convention still needs final handling during feature build | Yes, as explicit fallback if NRCC/CLIMOD file is unavailable |
| MRMS - Multi-Radar Multi-Sensor | https://mrms.nssl.noaa.gov and https://registry.opendata.aws/noaa-mrms-pds/ | Future spatial rainfall source | Deferred future source | Gridded precipitation rates and accumulations | Best future option for sewershed-weighted rainfall once North River geometry is available | Requires sewershed boundary / Appendix G; not for current V1 | No, deferred |

## C. Tide / Water-Level Source

| Source | URL | Project Role | Status | Variables / Information Of Interest | Reason For Inclusion | Limitations | Approved For Version 1 Production Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NOAA CO-OPS Station 8518750, The Battery | https://tidesandcurrents.noaa.gov/stationhome.html?id=8518750 | Primary Version 1 tide / water-level source | Selected | Observed water level, datum, units, station metadata | Best Version 1 proxy for lower Hudson / New York Harbor tidal conditions near Manhattan | Proxy only; not a plant-specific hydraulic boundary condition | Yes |

## D. Optional / Future Hydrometeorological Sources

| Source | URL | Project Role | Status | Variables / Information Of Interest | Reason For Inclusion | Limitations | Approved For Version 1 Production Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ERA5-Land | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land | Future hydrologic/weather supplement | Deferred future source | Temperature, precipitation, runoff, soil moisture, evaporation, snow, radiation | Useful future comparison or broader hydrologic-state context | Coarser than MRMS for NYC rainfall; not aligned with V1 DEP gauge logic | No, deferred |
| USGS Water Data API | https://api.waterdata.usgs.gov | Future exploratory hydraulic source | Deferred future source | River stage, groundwater, streamflow, water quality, precipitation where available | Could provide supplemental hydrologic or river-stage context if relevant stations are found | No directly relevant North River station identified yet | No, deferred |

## E. Reference-Only / Not-For-Modeling Sources

| Source | URL | Project Role | Status | Variables / Information Of Interest | Reason For Inclusion | Limitations | Approved For Version 1 Production Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| George Washington Bridge tide forecast | https://www.tide-forecast.com/locations/George-Washington-Bridge-New-York/tides/latest | Visualization / intuition only | Reference only | Tide forecasts, high/low timing | Useful for qualitative Hudson tide timing intuition | Not preferred for reproducible data ingestion or ML features | No |

## F. Future Target / Context Sources

| Source | URL | Project Role | Status | Variables / Information Of Interest | Reason For Inclusion | Limitations | Approved For Version 1 Production Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NYC DEP Wastewater Treatment Plant Performance Data | https://data.cityofnewyork.us/Environment/Wastewater-Treatment-Plant-Performance-Data/hgue-hj96/about_data | Future target/context screening | Context source only | Plant-level performance and possibly flow-related metrics | Useful to understand public plant performance data | Likely not hourly North River influent-flow target data | No |
| Future real hourly North River influent-flow source | To be obtained | Future model target source | Not available | Actual hourly `influent_flow_mgd` | Required for model-table construction and supervised ML | Not currently available; do not synthesize | No for V1; required for future model table |

## Recommended Use By Project Phase

| Phase | Rainfall | Temperature | Tides | Other Sources | Purpose |
| --- | --- | --- | --- | --- | --- |
| Version 1 feature store | NRCC/Central Park if manually acquired; otherwise NOAA LCD fallback Central Park hourly precipitation | NOAA LCD if useful and non-blocking | NOAA CO-OPS 8518750 The Battery | DEP reports for methodology | Build first local hourly external-forcing dataframe |
| Version 2 model table | Same rainfall source as V1 unless improved | NOAA LCD | NOAA Battery | Real hourly North River influent flow if obtained | Join actual influent target and train first baseline model |
| Future spatial rainfall | MRMS sewershed-average rainfall | NOAA LCD / ERA5-Land | NOAA Battery | Appendix G / sewershed boundary | Move from point rainfall to spatially distributed rainfall features |
