"""Download the latest data."""
import sys

import pandas as pd

url = "https://raw.githubusercontent.com/palewire/noaa-hurricane-gis-scraper/main/data/consolidated/adecks.csv"
df = pd.read_csv(url, parse_dates=["datetime"])

df = df.sort_values("datetime", ascending=False)

df.head(25).to_json(sys.stdout, orient="records", date_format="iso", indent=2)
