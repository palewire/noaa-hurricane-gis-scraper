"""Common utilities for this library."""
from __future__ import annotations

import collections
import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

import feedparser
import geojson
import geopandas as gpd
import kml2geojson
import pandas as pd
import requests
from pyogrio import set_gdal_config_options
from retry import retry
from rich import print

# Set the GDAL configuration options
set_gdal_config_options(
    {
        "SHAPE_RESTORE_SHX": "YES",  # Restore .shx file if missing
    }
)


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


def convert_adeck(adeck_path: Path, verbose: bool = True) -> dict:
    """Convert the submitted A-Deck CSV file to geojson.

    Args:
        adeck_path: The path to the A-Deck CSV file (Path)
        verbose: Whether to print the path being saved (bool)

    Returns:
        The geojson (Any)
    """
    # Read in the file
    df = pd.read_csv(
        adeck_path,
        usecols=[
            "YYYYMMDDHH",
            "TECH",
            "TECHNUM/MIN",
            "TAU",
            "LATN/S",
            "LONE/W",
        ],
        dtype=str,
    )

    # Clean up the columns
    def _clean_x(lon: str) -> float:
        if "W" in lon:
            lon_temp = lon.split("W")[0]
            val = round(float(lon_temp) * -0.1, 1)
        elif "E" in lon:
            lon_temp = lon.split("E")[0]
            val = round(float(lon_temp) * 0.1, 1)
        return val

    def _clean_y(lat: str) -> float:
        if "N" in lat:
            lat_temp = lat.split("N")[0]
            val = round(float(lat_temp) * 0.1, 1)
        elif "S" in lat:
            lat_temp = lat.split("S")[0]
            val = round(float(lat_temp) * -0.1, 1)
        return val

    def _parse_dt(dt: str) -> datetime:
        return datetime.strptime(dt, "%Y%m%d%H")

    df["x"] = df["LONE/W"].apply(_clean_x)
    df["y"] = df["LATN/S"].apply(_clean_y)
    df["warning_datetime"] = df.YYYYMMDDHH.apply(_parse_dt)
    df["forecast_hour"] = df.TAU.apply(int)

    # Trim the dataframe
    trimmed_df = df[["warning_datetime", "TECH", "forecast_hour", "x", "y"]].rename(
        columns={"TECH": "model"}
    )

    # Convert to GeoJSON
    feature_dict: dict[str, dict] = collections.defaultdict(dict)
    for model in trimmed_df["model"].unique():
        feature_dict[model] = collections.defaultdict(list)

    for record in trimmed_df.sort_values(
        ["model", "warning_datetime", "forecast_hour"]
    ).to_dict(orient="records"):
        # Nest another level of lists to group by model and warning_datetime
        feature_dict[record["model"]][record["warning_datetime"]].append(record)

    feature_list = []
    for model, dt_list in feature_dict.items():
        for dt, value_list in dt_list.items():
            coords = [(d["x"], d["y"]) for d in value_list]
            geom = geojson.LineString(coords)
            feat = geojson.Feature(
                geometry=geom, properties=dict(model=model, warning_datetime=str(dt))
            )
            feature_list.append(feat)

    feat_collection = geojson.FeatureCollection(feature_list)

    # Return the GeoJSON as a Python dict
    return json.loads(geojson.dumps(feat_collection))


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
    gdf = gpd.read_file(str(shp_path), on_invalid="warn")

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
