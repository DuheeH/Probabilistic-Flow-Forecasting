# Source Register

This file tracks the main sources considered for the North River WRRF Version 1 feature store: what each source was for, what happened, and whether it belongs in V1.

## Methodology / Project Context

| Source | Role | Status | Reason | Limitation | V1 approved |
| --- | --- | --- | --- | --- | --- |
| NYC DEP InfoWorks Citywide Recalibration Report | Modeling context | Reviewed | Supports using rainfall source choices tied to DEP modeling context | Report, not time-series data | Yes, as context |
| NYC DEP Hydraulic Capacity Analysis Report, 2012 | Hydraulic context | Reviewed | Supports lagged rainfall, storage, routing, and wet-weather features | North River Appendix G is not available yet | Yes, as context |
| Appendix G - North River Hydraulic Capacity Analysis | Future North River-specific context | Requested via FOIL | May provide sewershed, regulator, interceptor, and hydraulic details | Not currently available | No, deferred |
| Monthly Operating Efficiency workbook | Monthly plant context | Preserved locally | Useful for broad context and sanity checks | Monthly data is not hourly influent-flow target data | No, context only |

## Rainfall Source Exploration

| Source | Role | Status | Reason | Limitation | V1 approved |
| --- | --- | --- | --- | --- | --- |
| NRCC NYC Weather Network / Central Park gauge | Preferred conceptual rainfall source | Preferred but not automated | Aligns with DEP/North River calibration logic | Gauge page was not straightforward for automated decade-scale hourly export | Not used directly |
| CLIMOD 2 | NRCC/Cornell source path | Investigated | Possible path for Central Park rainfall | Central Park metadata found, but hourly export not confirmed | No |
| ACIS / NOAA Regional Climate Centers | Direct RCC/ACIS check | Investigated | Confirmed Central Park metadata and daily precipitation | No usable hourly precipitation endpoint confirmed | No |
| NOAA/NCEI Local Climatological Data | Practical fallback rainfall source | Approved, downloaded, loader-tested | Provides Central Park hourly observations for station `USW00094728` | Fallback, not original preferred NRCC route; uses `FM-15` rows bucketed to hour | Yes |
| MRMS | Future spatial rainfall source | Deferred | Could support sewershed-average rainfall later | Needs sewershed geometry / Appendix G | No |

## Tide / Water Level

| Source | Role | Status | Reason | Limitation | V1 approved |
| --- | --- | --- | --- | --- | --- |
| NOAA CO-OPS Station 8518750, The Battery | Tide / water-level proxy | Downloaded and joined in V1 | Official hourly water-level station for New York Harbor / lower Hudson context | Proxy only; not a plant-specific hydraulic boundary | Yes |

## Optional / Future Hydrometeorology

| Source | Role | Status | Reason | Limitation | V1 approved |
| --- | --- | --- | --- | --- | --- |
| ERA5-Land | Future weather/hydrologic supplement | Deferred | Could help compare broader hydrologic conditions | Coarser than needed for V1 rainfall logic | No |
| USGS Water Data API | Future exploratory source | Deferred | Could provide river stage or groundwater context if relevant stations are found | No directly relevant North River station identified yet | No |

## Reference Only

| Source | Role | Status | Reason | Limitation | V1 approved |
| --- | --- | --- | --- | --- | --- |
| George Washington Bridge tide forecast | Qualitative tide reference | Reference only | Useful for intuition about Hudson tide timing | Not a reproducible data-ingestion source | No |

## Future Target / Context

| Source | Role | Status | Reason | Limitation | V1 approved |
| --- | --- | --- | --- | --- | --- |
| NYC DEP Wastewater Treatment Plant Performance Data | Public plant context | Context only | Useful to understand public performance data | Not assumed to be hourly North River influent-flow target data | No |
| Future real hourly North River influent-flow data | Model target | Not available | Required before supervised modeling | Do not synthesize | No for V1; required later |
