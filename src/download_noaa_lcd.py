"""Download NOAA/NCEI LCD Central Park yearly CSVs into one raw file.

This script implements the documented fallback source only. It does not build
the feature store and does not synthesize rainfall.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import requests


BASE_URL = "https://www.ncei.noaa.gov/oa/local-climatological-data/v2/access"
STATION_ID = "USW00094728"
DEFAULT_OUTPUT = Path(
    "data/raw/weather/central_park_noaa_lcd_hourly_weather_2015_2024.csv"
)


def yearly_url(year: int) -> str:
    return f"{BASE_URL}/{year}/LCD_{STATION_ID}_{year}.csv"


def download_lcd_years(start_year: int, end_year: int, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wrote_header = False

    with output_path.open("w", encoding="utf-8", newline="") as out:
        for year in range(start_year, end_year + 1):
            url = yearly_url(year)
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            lines = response.text.splitlines()
            if not lines:
                raise ValueError(f"No data returned for {year}: {url}")

            if not wrote_header:
                out.write(lines[0] + "\n")
                wrote_header = True
            for line in lines[1:]:
                out.write(line + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download NOAA LCD Central Park yearly CSVs and combine them."
    )
    parser.add_argument("--start-year", type=int, default=2015)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    download_lcd_years(args.start_year, args.end_year, args.output)
    print(f"Saved NOAA LCD fallback rainfall file to: {args.output}")


if __name__ == "__main__":
    main()
