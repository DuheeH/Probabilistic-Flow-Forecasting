# Source Code

Scripts in this folder build Version 1 external-forcing features only.

- `download_noaa_lcd.py`: downloads the NOAA LCD Central Park fallback rainfall file.
- `rainfall_loader.py`: loads and standardizes Central Park rainfall.
- `build_feature_store_v1.py`: downloads/loads Battery tide data and builds the V1 feature store.

No model training happens here yet. Do not add flow targets or flow-lag features until real hourly North River influent-flow data is available.
