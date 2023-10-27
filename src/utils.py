"""Common utilities for this library."""
from __future__ import annotations

import json
from typing import Any

import requests
import feedparser
from retry import retry


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
    return requests.get(url)


def write_json(data: Any, out_path: str, indent: int = 4, verbose: bool = True) -> None:
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

    # Dump all of the entry data to a json file
    with open(out_path, "w") as f:
        if verbose:
            print(f"Saving {out_path}")
        json.dump(data, f, indent=4, sort_keys=True)