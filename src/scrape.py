"""Scrape GIS data from NOAA's RSS feeds."""
from __future__ import annotations

import gzip
import zipfile
from pathlib import Path

import click
from bs4 import BeautifulSoup
from rich import print

from . import utils

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent / "data" / "raw"
DUMMY_URL = "https://www.nhc.noaa.gov/gis/"


@click.group()
def scrape() -> None:
    """Scrape data posted online by NOAA."""
    pass


@scrape.command()
def adecks() -> None:
    """Scrape the adeck file archive."""
    # Get the url
    url = "https://ftp.nhc.noaa.gov/atcf/aid_public/"
    r = utils.get_url(url)

    # Parse out the links
    soup = BeautifulSoup(r.content, "lxml")
    link_list = soup.find_all("a")[4:]

    # Loop through the links
    for link in link_list:
        href = link.get("href")
        if href == "../":
            continue

        # Set the download location
        out_dir = DATA_DIR / f"adeck-{href.replace('.dat.gz', '')}"

        # Make the directory
        out_dir.mkdir(exist_ok=True, parents=True)

        # Get the URL
        r = utils.get_url(url + href, verbose=True)

        # Save the file in the out_dir
        path = out_dir / Path(href).name
        with open(path, "wb") as f:
            f.write(r.content)

        # Unzip the gzip file in the out_dir with gzip
        print(f"Unzipping {path}")
        with gzip.open(path, "rb") as zip_ref:
            content = zip_ref.read()
            with open(out_dir / Path(href).name.replace(".gz", ""), "wb") as f:
                f.write(content)


@scrape.command()
def archive() -> None:
    """Scrape the archive's HTML index."""
    # Get the URL
    url = "https://www.nhc.noaa.gov/gis/forecast/archive/"
    r = utils.get_url(url)

    # Parse out the links
    soup = BeautifulSoup(r.content, "lxml")
    link_list = soup.find_all("a")[5:]

    # Loop through the links
    for link in link_list:
        href = link.get("href")
        if href == "../":
            continue

        # Get the filename from the stem
        filename = Path(href).stem

        # Set the download location
        out_dir = DATA_DIR / filename

        # If the file already exists, skip the download
        if out_dir.exists():
            continue

        # Make the directory
        out_dir.mkdir(exist_ok=True, parents=True)

        # Get the URL
        r = utils.get_url(url + href, verbose=True)

        # Save the file in the out_dir
        path = out_dir / Path(href).name
        with open(path, "wb") as f:
            f.write(r.content)

        # If it's a zip file, unzip it
        if str(path).endswith(".zip") or str(path).endswith(".kmz"):
            print(f"Unzipping {path}")
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(out_dir)


@scrape.command()
def feeds() -> None:
    """Scrape GIS data from NOAA's RSS feeds."""
    rss_list = [
        "https://www.nhc.noaa.gov/gis-at.xml",
        "https://www.nhc.noaa.gov/gis-ep.xml",
        "https://www.nhc.noaa.gov/gis-cp.xml",
    ]
    for rss in rss_list:
        d = utils.get_rss_url(rss)
        for entry in d.entries:
            if entry.id == DUMMY_URL:
                continue

            # Write out the entry
            this_dir = DATA_DIR / entry.id
            utils.write_json(entry, this_dir / "item.json")

            # Loop through the links
            for link in entry.links:
                if link.href == DUMMY_URL:
                    continue

                # Download the file
                r = utils.get_url(link.href)

                # Save the file
                path = this_dir / link.href.split("/")[-1]
                with open(path, "wb") as f:
                    f.write(r.content)

                # If it's a zip file, unzip it
                if str(path).endswith(".zip") or str(path).endswith(".kmz"):
                    print(f"Unzipping {path}")
                    with zipfile.ZipFile(path, "r") as zip_ref:
                        zip_ref.extractall(this_dir)


if __name__ == "__main__":
    scrape()
