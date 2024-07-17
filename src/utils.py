"""Common utilities for this library."""
from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import feedparser
import geopandas as gpd
import kml2geojson
import requests
from retry import retry
from rich import print
from pyogrio import set_gdal_config_options

# Set the GDAL configuration options
set_gdal_config_options({
    'SHAPE_RESTORE_SHX': 'YES',  # Restore .shx file if missing
})


@retry(tries=3, delay=5)
def get_rss_url(url: str, verbose: bool = True) -> feedparser.FeedParserDict:
    """Download an RSS file.

    Args:
        url: The URL to download (str)
        verbose: Whether to print the path being saved (bool)

    Returns:
        The RSS feed (feedparser.FeedParserDict)
    """
    if verbose:
        print(f"Fetching {url}")
    return feedparser.parse(url)


@retry(tries=3, delay=5)
def get_url(url: str, verbose: bool = True) -> requests.Response:
    """Download a file.

    Args:
        url: The URL to download (str)
        verbose: Whether to print the path being saved (bool)

    Returns:
        The file (requests.Response)
    """
    if verbose:
        print(f"Fetching {url}")
    return requests.get(url, timeout=30)


def write_json(
    data: Any, out_path: Path, indent: int = 4, verbose: bool = True
) -> None:
    """Write a dictionary to a JSON file.

    Args:
        data: The data to write (Any)
        out_path: The path to write the data to (str)
        indent: The number of spaces to indent the JSON file (int)
        verbose: Whether to print the path being saved (bool)

    Returns:
        None
    """
    # Ensure we have the directory to save the file
    out_dir = out_path.parent
    out_dir.mkdir(exist_ok=True, parents=True)

    # Make sure the filename and extension are both lowercase
    out_path = out_path.with_name(out_path.name.lower())

    # Dump all of the entry data to a json file
    with open(out_path, "w") as f:
        if verbose:
            print(f"Saving {out_path}")
        json.dump(data, f, indent=4, sort_keys=True)


def convert_shp(shp_path: Path, verbose: bool = True) -> dict:
    """Convert the submitted shapefile to geojson.

    Args:
        shp_path: The path to the shapefile (Path)
        verbose: Whether to print the path being saved (bool)

    Returns:
        The geojson (Any)

    Examples:
        >>> from pathlib import Path
        >>> from src import utils
        >>> shp_path = Path("data/raw/AL112020_5day_pgn.shp")
        >>> geojson = utils.convert_shp(shp_path)
    """
    # Read in the file with geopandas
    if verbose:
        print(f"Reading {shp_path}")
    gdf = gpd.read_file(str(shp_path))

    # Ignore any UserWarnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Convert the geopandas dataframe to geojson
        if verbose:
            print(f"Converting {shp_path} to GeoJSON")
        json_data = gdf.to_json(indent=4)

    # Return it as a python object
    return json.loads(json_data)


def convert_kml(kml_path: Path) -> dict:
    """Convert the submitted kml file to geojson.

    Args:
        kml_path: The path to the kml file (Path)

    Returns:
        The geojson (Any)

    Examples:
        >>> from pathlib import Path
        >>> from src import utils
        >>> kml_path = Path("data/raw/AL112020_5day_pgn.kml")
        >>> geojson = utils.convert_kml(kml_path)
    """
    geojson_list = kml2geojson.convert(
        str(kml_path),
        style_type=None,
        separate_folders=False,
    )
    assert len(geojson_list) == 1
    return geojson_list[0]
