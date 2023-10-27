"""Convert raw NOAA data into GeoJSON files."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
import warnings

import click
import geopandas as gpd

from . import utils

THIS_DIR = Path(__file__).parent
RAW_DIR = THIS_DIR.parent / "data" / "raw"
PROCESSED_DIR = THIS_DIR.parent / "data" / "processed"


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
        print(f"Copying {item_path} to {processed_path}")
        shutil.copy(item_path, processed_path)

        # Get a list of all files in the raw directory with glob
        raw_files = this_raw_dir.glob("*")

        # Loop through the files:
        for f in raw_files:
            # If it's a .shp file ...
            if str(f).endswith(".shp"):
                # Read it in with geopandas
                gdf = gpd.read_file(str(f))

                # Set the output path for a geojson output
                geojson_path = this_processed_dir / f"{f.stem}.geojson"

                # Ignore any UserWarnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    # Convert the geopandas dataframe to geojson
                    json_data = gdf.to_json(indent=4)

                # Write it out
                utils.write_json(json.loads(json_data), geojson_path)

            # If it's a KML file
            elif str(f).endswith(".kml"):
                # Set the output path for a geojson output
                geojson_path = this_processed_dir / f"{f.stem}.geojson"

                # Convert it with ogr2ogr
                print(f"Converting {f} to {geojson_path}")
                command = ['ogr2ogr', '-f', 'GeoJSON', str(geojson_path), str(f)]
                subprocess.run(command)

            # If it's a KMZ file
            elif str(f).endswith(".kmz"):
                # Set the output path for a geojson output
                geojson_path = this_processed_dir / f"{f.stem}.geojson"

                # Convert it with ogr2ogr
                print(f"Converting {f} to {geojson_path}")
                command = ['ogr2ogr', '-f', 'GeoJSON', str(geojson_path), str(f)]
                subprocess.run(command)



if __name__ == "__main__":
    convert()