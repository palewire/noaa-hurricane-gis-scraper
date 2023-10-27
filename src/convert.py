"""Convert raw NOAA data into GeoJSON files."""
from __future__ import annotations

import shutil
from pathlib import Path

import click

from . import utils

THIS_DIR = Path(__file__).parent
RAW_DIR = THIS_DIR.parent / "data" / "raw"
PROCESSED_DIR = THIS_DIR.parent / "data" / "processed"


@click.command()
def convert() -> None:
    """Convert raw NOAA data into GeoJSON files."""
    # Get a list of all folders in the raw directory
    raw_dirs = [x for x in RAW_DIR.iterdir() if x.is_dir()]

    # Loop through them
    for this_raw_dir in raw_dirs:
        # Extract the id from the name of the directory
        storm_id = this_raw_dir.name

        # Check if the same id exists in the processed directory
        this_processed_dir = PROCESSED_DIR / storm_id

        # If it doesn't make it
        if not this_processed_dir.exists():
            this_processed_dir.mkdir(parents=True)

        # Copy the item.json file to the processed directory
        item_path = this_raw_dir / "item.json"
        processed_path = this_processed_dir / item_path.name
        shutil.copy(item_path, processed_path)

        # Get a list of all files in the raw directory with glob
        raw_files = this_raw_dir.glob("*")

        # Loop through the files:
        for f in raw_files:
            # If it's a .shp file ...
            if str(f).endswith(".shp"):
                # Set the output path for a geojson output
                geojson_path = this_processed_dir / f"{f.stem}.geojson"

                # Read it in with geopandas
                geojson = utils.convert_shp(f)

                # Write it out
                utils.write_json(geojson, geojson_path)

            # If it's a KML file
            elif str(f).endswith(".kml"):
                # Set the output path for a geojson output
                geojson_path = this_processed_dir / f"{f.stem}.geojson"

                # Read it in as a KML
                geojson = utils.convert_kml(f)

                # Write out the result
                utils.write_json(geojson, geojson_path)


if __name__ == "__main__":
    convert()
