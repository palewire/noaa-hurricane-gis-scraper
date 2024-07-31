Automated downloads of geographic information system data posted by the National Oceanic and Atmospheric Administration's National Hurricane Center and Central Pacific Hurricane Center

## Installation

Clone the repository.

```bash
gh repo clone palewire/noaa-hurricane-gis-scraper
```

Move into the directory.

```bash
cd noaa-hurricane-gis-scraper
```

Install the requirements.

```bash
pipenv install --dev`
```

## Usage

Scrape GIS feeds.

```bash
pipenv run python -m pipeline.scrape feeds
```

Scrape a-deck models.

```bash
pipenv run python -m pipeline.scrape adecks
```

Convert GIS feeds to GeoJSON.

```bash
pipenv run python -m pipeline.convert maps
```

Convert a-deck models to GeoJSON.

```bash
pipenv run python -m pipeline.convert adecks
```

Consolidate a master list of processed a-deck files.

```bash
pipenv run python -m pipeline.consolidate adecks
```
