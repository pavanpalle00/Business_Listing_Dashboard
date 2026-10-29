"""One command for the whole data pipeline.

    python -m scraper.run_pipeline              # scrape + clean
    python -m scraper.run_pipeline --upload     # scrape + clean + upload to API
    python -m scraper.run_pipeline --skip-scrape --upload   # re-clean & upload only
"""
import argparse
import logging

from . import cleaner, osm_scraper, uploader, wikipedia_scraper
from .config import API_BASE_URL


def main() -> None:
    parser = argparse.ArgumentParser(description="Business listings data pipeline")
    parser.add_argument("--skip-scrape", action="store_true", help="reuse existing scraped JSON files")
    parser.add_argument("--upload", action="store_true", help="POST the cleaned data to the API")
    parser.add_argument("--api", default=API_BASE_URL, help="FastAPI base URL")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    if not args.skip_scrape:
        osm_scraper.scrape()
        wikipedia_scraper.scrape()
    cleaner.run()
    if args.upload:
        uploader.upload(args.api)


if __name__ == "__main__":
    main()
