"""Convert raw NOAA data into GeoJSON files."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import click
import geopandas as gpd

from . import utils

THIS_DIR = Path(__file__).parent
RAW_DIR = THIS_DIR.parent / "data" / "raw"
PROCESSED_DIR = THIS_DIR.parent / "data" / "processed"


@click.group()
def convert() -> None:
    """Convert raw NOAA data into more useful files."""
    pass


@convert.command()
def adecks() -> None:
    """Convert adeck CSVs into GeoJSON."""
    # Get a glob list of all files that end with .csv in folders that start with adeck-
    adeck_files = list(RAW_DIR.glob("adeck-*/*.csv"))

    # Loop through them
    for f in adeck_files:
        # Extract the id from the name of the directory
        geojson = utils.convert_adeck(f)

        # Now read in the geojson as a geodataframe
        gdf = gpd.read_file(json.dumps(geojson), on_invalid="warn")

        # Loop through the distinct warning_datetime
        for dt in gdf["warning_datetime"].unique():
            # Filter the geodataframe to that timestamp
            this_gdf = gdf[gdf["warning_datetime"] == dt].copy()

            # Set the output path for timestamped geojson
            geojson_path = (
                PROCESSED_DIR
                / f"{f.parent.name}"
                / f"{f.stem.lower()}-{dt.strftime('%Y%m%d-%H%M')}.geojson"
            )

            # Convert warning_datetime to string
            this_gdf["warning_datetime"] = this_gdf["warning_datetime"].astype(str)

            # Write out the result as a smaller file with just that timestamp
            utils.write_json(json.loads(this_gdf.to_json(indent=4)), geojson_path)


@convert.command()
def maps() -> None:
    """Convert the map files into GeoJSON."""
    # Get a list of all folders in the raw directory
    raw_dirs = [x for x in RAW_DIR.iterdir() if x.is_dir()]

    # Loop through them
    for this_raw_dir in raw_dirs:
        # Extract the id from the name of the directory
        storm_id = this_raw_dir.name

        # Check if the same id exists in the processed directory ...
        this_processed_dir = PROCESSED_DIR / storm_id

        # ... if it doesn't make it.
        if not this_processed_dir.exists():
            this_processed_dir.mkdir(parents=True)

        # Copy the item.json file to the processed directory, if it exists.
        item_path = this_raw_dir / "item.json"
        if item_path.exists():
            processed_path = this_processed_dir / item_path.name
            shutil.copy(item_path, processed_path)

        # Get a list of all files in the raw directory with glob ...
        raw_files = sorted(list(this_raw_dir.glob("*")))

        # ... and filter it down to files that are either .shp or .kml.
        map_files = [x for x in raw_files if x.suffix in [".shp", ".kml"]]

        # Loop through the files:
        for f in map_files:
            # Set the output path for geojson.
            geojson_path = this_processed_dir / f"{f.stem.lower()}.geojson"

            # If the file already exists, skip this iteration.
            if geojson_path.exists():
                continue

            # If it's a .shp file ...
            if str(f).endswith(".shp"):
                # ... read it in with geopandas.
                geojson = utils.convert_shp(f)

            # If it's a KML file ...
            elif str(f).endswith(".kml"):
                # ... read it in as a KML.
                geojson = utils.convert_kml(f)

            # Write out the result.
            utils.write_json(geojson, geojson_path)


if __name__ == "__main__":
    convert()
