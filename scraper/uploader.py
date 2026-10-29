"""Send the cleaned listings to the FastAPI bulk-insert endpoint.

The scraper never talks to MySQL directly: the API is the single gateway to
the database, so validation and duplicate handling live in one place.

Run:  python -m scraper.uploader [--api http://localhost:8000]
"""
import argparse
import json
import logging

import requests

from . import config

log = logging.getLogger(__name__)


def batches(rows: list[dict], size: int):
    for start in range(0, len(rows), size):
        yield rows[start:start + size]


def upload(api_base: str = config.API_BASE_URL, batch_size: int = config.UPLOAD_BATCH_SIZE) -> dict:
    rows = json.loads(config.CLEAN_JSON.read_text(encoding="utf-8"))
    url = f"{api_base.rstrip('/')}/api/listings/bulk"
    totals = {"received": 0, "inserted": 0, "duplicates_skipped": 0}

    for number, batch in enumerate(batches(rows, batch_size), start=1):
        response = requests.post(url, json={"listings": batch}, timeout=60)
        if response.status_code != 201:
            raise RuntimeError(f"batch {number} failed: {response.status_code} {response.text}")
        result = response.json()
        for key in totals:
            totals[key] += result[key]
        log.info("batch %d: %s", number, result)

    log.info("upload finished: %s", totals)
    return totals


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default=config.API_BASE_URL, help="FastAPI base URL")
    upload(parser.parse_args().api)
