"""Scrape GIS data from NOAA's RSS feeds."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import click
import feedparser
import requests
from rich import print

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
        print(f"Fetching {rss}")
        d = feedparser.parse(rss)
        for entry in d.entries:
            if entry.id == "https://www.nhc.noaa.gov/gis/":
                continue

            # Get the directory reader to save the file
            entry_dir = DATA_DIR / entry.id
            entry_dir.mkdir(exist_ok=True, parents=True)

            # Dump all of the entry data to a json file
            with open(entry_dir / "item.json", "w") as f:
                print(f"Saving {entry_dir / 'item.json'}")
                json.dump(entry, f, indent=4)

            # Loop through the links
            for link in entry.links:
                if link.href == "https://www.nhc.noaa.gov/gis/":
                    continue

                # Get the filename
                filename = link.href.split("/")[-1]

                # Get the full path
                path = entry_dir / filename

                # Download the file
                print(f"Downloading {path}")
                r = requests.get(link.href)

                # Save the file
                with open(path, "wb") as f:
                    f.write(r.content)

                # If it's a zip file, unzip it
                if filename.endswith(".zip"):
                    print(f"Unzipping {path}")
                    with zipfile.ZipFile(path, "r") as zip_ref:
                        zip_ref.extractall(entry_dir)


if __name__ == "__main__":
    scrape()
