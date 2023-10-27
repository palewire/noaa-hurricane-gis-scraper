"""Scrape GIS data from NOAA's RSS feeds."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import click
import requests
from rich import print

from . import utils

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent / "data" / "raw"


@click.command()
def scrape() -> None:
    """Scrape GIS data from NOAA's RSS feeds."""
    rss_list = [
        "https://www.nhc.noaa.gov/gis-at.xml",
        "https://www.nhc.noaa.gov/gis-ep.xml",
        "https://www.nhc.noaa.gov/gis-cp.xml",
    ]
    for rss in rss_list:
        d = utils.get_rss_url(rss)
        for entry in d.entries:
            if entry.id == "https://www.nhc.noaa.gov/gis/":
                continue

            # Write out the entry
            utils.write_json(entry, DATA_DIR / entry.id / "item.json")

            # Loop through the links
            for link in entry.links:
                if link.href == "https://www.nhc.noaa.gov/gis/":
                    continue

                # Get the filename
                filename = link.href.split("/")[-1]

                # Download the file
                r = utils.get_url(link.href)

                # Save the file
                with open(DATA_DIR / entry.id / filename, "wb") as f:
                    f.write(r.content)

                # If it's a zip file, unzip it
                if filename.endswith(".zip"):
                    print(f"Unzipping {path}")
                    with zipfile.ZipFile(path, "r") as zip_ref:
                        zip_ref.extractall(entry_dir)


if __name__ == "__main__":
    scrape()
