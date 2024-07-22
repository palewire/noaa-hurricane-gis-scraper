"""Commands for consolidating scraped data into organized feeds."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import click
import pandas as pd
from rich import print

THIS_DIR = Path(__file__).parent
RAW_DIR = THIS_DIR.parent / "data" / "raw"
PROCESSED_DIR = THIS_DIR.parent / "data" / "processed"
CONSOLIDATED_DIR = THIS_DIR.parent / "data" / "consolidated"


@click.group()
def consolidate() -> None:
    """Consolidate scraped data into organized feeds."""
    pass


@consolidate.command()
def adecks() -> None:
    """Consolidate adeck GeoJSON files into a single GeoJSON file."""
    # Get a glob list of all the adeck directories
    adeck_dirs = list(PROCESSED_DIR.glob("adeck-*"))

    # Extract the ids from the folder names, which come after the adeck- prefix
    ids = [d.name.split("-")[1] for d in adeck_dirs]

    # Print out how many unique adecks we have
    print(f"Found {len(ids)} unique adecks.")

    # Get a list to hold all the processed files
    processed_files = []

    # Loop through the adeck ids
    for id in ids:
        # Get a list of all the GeoJSON files for this adeck
        adeck_files = list(PROCESSED_DIR.glob(f"adeck-{id}/*.geojson"))

        # Loop through the GeoJSON files
        for f in adeck_files:
            # Parse the date and time from the filename
            dt_str = "-".join(f.stem.split("-")[1:])

            # Convert it to a datetime object
            dt = datetime.strptime(dt_str, "%Y%m%d-%H%M")

            # Compose the raw GitHub hosted URL to the geojson of that name
            geojson_url = f"https://raw.githubusercontent.com/palewire/noaa-hurricane-gis-scraper/main/data/processed/adeck-{id}/{f.stem}.geojson"

            # Compose the URL for the raw dat, dat.gz and CSV files
            csv_url = f"https://raw.githubusercontent.com/palewire/noaa-hurricane-gis-scraper/main/data/raw/adeck-{id}/{id}.csv"
            dat_url = f"https://raw.githubusercontent.com/palewire/noaa-hurricane-gis-scraper/main/data/raw/adeck-{id}/{id}.dat"
            dat_gz_url = f"https://raw.githubusercontent.com/palewire/noaa-hurricane-gis-scraper/main/data/raw/adeck-{id}/{id}.dat.gz"

            # Append the processed file to the list
            processed_files.append(
                {
                    "id": id,
                    "datetime": dt,
                    "geojson_url": geojson_url,
                    "csv_url": csv_url,
                    "dat_url": dat_url,
                    "dat_gz_url": dat_gz_url,
                }
            )

    # Read in a a dataframe
    df = pd.DataFrame(processed_files)
    print(f"Consolidated {len(df)} files.")

    # Sort in reverse chronological order
    df = df.sort_values("datetime", ascending=False)

    # Write out the processed files as a CSV file
    CONSOLIDATED_DIR.mkdir(exist_ok=True, parents=True)
    csv_path = CONSOLIDATED_DIR / "adecks.csv"
    df.to_csv(csv_path, index=False)
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    consolidate()
