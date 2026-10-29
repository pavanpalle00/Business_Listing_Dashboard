"""Source 2 - Wikipedia business pages, parsed from HTML with BeautifulSoup.

Two steps:
1. The MediaWiki API lists every article in a category such as
   "Hospitals in Chennai" (structured JSON, no HTML involved).
2. For each article we download the rendered HTML and *scrape* the infobox
   (the summary table on the right of the article) with BeautifulSoup to get
   the address and phone number.

Wikipedia content is CC BY-SA licensed and its API is meant for programmatic
access, so this is a ToS-friendly way to demonstrate real HTML scraping.

Run:  python -m scraper.wikipedia_scraper
"""
import json
import logging
import re

from bs4 import BeautifulSoup

from . import config
from .http_client import PoliteClient

log = logging.getLogger(__name__)

SOURCE_NAME = "Wikipedia"

ADDRESS_LABELS = ("address", "location")
PHONE_LABELS = ("phone", "telephone", "contact")
CITATION = re.compile(r"\[\d+\]|\[citation needed\]", re.I)
SKIP_TITLE_PREFIXES = ("List of", "Lists of")


def list_category_pages(client: PoliteClient, category: str) -> list[str]:
    """Return the titles of all articles (namespace 0) in a Wikipedia category."""
    titles: list[str] = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmtype": "page",
        "cmnamespace": 0,
        "cmlimit": 500,
        "format": "json",
    }
    while True:
        data = client.get(config.WIKI_API, params=params).json()
        titles += [m["title"] for m in data["query"]["categorymembers"]]
        if "continue" not in data:  # API pagination
            return [t for t in titles if not t.startswith(SKIP_TITLE_PREFIXES)]
        params.update(data["continue"])


def fetch_article_html(client: PoliteClient, title: str) -> str:
    data = client.get(config.WIKI_API, params={
        "action": "parse",
        "page": title,
        "prop": "text",
        "section": 0,          # only the lead section - that's where the infobox is
        "redirects": 1,
        "format": "json",
        "formatversion": 2,
    }).json()
    return data.get("parse", {}).get("text", "")


def clean_text(node) -> str:
    """Infobox cell -> plain text without citations or hidden spans."""
    for tag in node.select("sup, style, .noprint, .geo-inline-hidden"):
        tag.decompose()
    text = node.get_text(" ", strip=True)
    text = CITATION.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"\s+([,;.)])", r"\1", text).strip(" ,;")  # get_text(" ") adds "Adyar , Chennai"


def parse_infobox(html: str) -> dict[str, str]:
    """Scrape the infobox table into {label: value}, e.g. {"address": "..."}."""
    soup = BeautifulSoup(html, "lxml")
    infobox = soup.select_one("table.infobox")
    if infobox is None:
        return {}
    fields: dict[str, str] = {}
    for row in infobox.select("tr"):
        label, value = row.find("th"), row.find("td")
        if label and value:
            key = clean_text(label).lower()
            fields.setdefault(key, clean_text(value))
    return fields


def pick(fields: dict[str, str], labels: tuple[str, ...]) -> str | None:
    for key, value in fields.items():
        if any(key.startswith(label) for label in labels) and value:
            return value
    return None


def display_name(title: str) -> str:
    """'Apollo Hospital (Chennai)' -> 'Apollo Hospital'."""
    return re.sub(r"\s*\([^)]*\)$", "", title).strip()


def scrape() -> list[dict]:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = config.RAW_DIR / "wikipedia_infoboxes.json"
    cache: dict[str, dict] = (
        json.loads(cache_file.read_text(encoding="utf-8")) if cache_file.exists() else {}
    )

    client = PoliteClient(delay=0.5)
    listings: list[dict] = []

    for category, city, wiki_category in config.WIKI_CATEGORIES:
        titles = list_category_pages(client, wiki_category)
        log.info("[%s] %d articles", wiki_category, len(titles))

        for title in titles:
            if title not in cache:
                try:
                    cache[title] = parse_infobox(fetch_article_html(client, title))
                except Exception as exc:
                    log.warning("skipping %r: %s", title, exc)
                    continue
            fields = cache[title]
            listings.append({
                "business_name": display_name(title),
                "category": category,
                "city": city,
                "address": pick(fields, ADDRESS_LABELS),
                "phone": pick(fields, PHONE_LABELS),
                "source": SOURCE_NAME,
            })

        # save progress after every category so a crash loses little work
        cache_file.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    config.WIKI_OUTPUT.write_text(json.dumps(listings, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Wikipedia: %d listings -> %s", len(listings), config.WIKI_OUTPUT)
    return listings


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    scrape()
