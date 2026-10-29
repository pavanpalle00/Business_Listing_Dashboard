"""Source 1 - OpenStreetMap business listings via the Overpass API.

OpenStreetMap is an open, crowd-sourced map whose data is licensed under the
ODbL, so collecting it is explicitly allowed (with attribution). The Overpass
API lets us ask questions such as "every named hospital inside this bounding
box that has a street address".

Run:  python -m scraper.osm_scraper
"""
import json
import logging

from . import config
from .http_client import PoliteClient

log = logging.getLogger(__name__)

SOURCE_NAME = "OpenStreetMap"


def build_query(bbox: tuple[float, float, float, float]) -> str:
    """Build one Overpass QL query that returns every category for one city.

    Each category is its own statement followed by its own ``out`` so the
    per-category limit is applied independently. ``["name"]["addr:street"]``
    keeps only businesses that have a name *and* a street address.
    """
    south, west, north, east = bbox
    box = f"({south},{west},{north},{east})"
    parts = ["[out:json][timeout:120];"]
    for key, value in config.OSM_CATEGORIES.values():
        parts.append(f'nwr["{key}"="{value}"]["name"]["addr:street"]{box};')
        parts.append(f"out tags {config.OSM_LIMIT_PER_CATEGORY};")
    return "\n".join(parts)


def fetch_city(client: PoliteClient, city: str, bbox) -> list[dict]:
    """Return raw Overpass elements for a city, using a local cache if present."""
    cache_file = config.RAW_DIR / f"osm_{city.lower()}.json"
    if cache_file.exists():
        log.info("[%s] using cached response %s", city, cache_file.name)
        return json.loads(cache_file.read_text(encoding="utf-8"))["elements"]

    query = build_query(bbox)
    for endpoint in config.OVERPASS_ENDPOINTS:
        try:
            log.info("[%s] querying %s", city, endpoint)
            response = client.post(endpoint, data={"data": query})
            payload = response.json()
            cache_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            return payload["elements"]
        except Exception as exc:  # try the next mirror
            log.warning("[%s] %s failed: %s", city, endpoint, exc)
    raise RuntimeError(f"All Overpass endpoints failed for {city}")


def detect_category(tags: dict) -> str | None:
    for label, (key, value) in config.OSM_CATEGORIES.items():
        if tags.get(key) == value:
            return label
    return None


def build_address(tags: dict) -> str | None:
    """Join the OSM ``addr:*`` tags into one human-readable address line."""
    if tags.get("addr:full"):
        return tags["addr:full"]
    parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:housename"),
        tags.get("addr:street"),
        tags.get("addr:place"),
        tags.get("addr:suburb") or tags.get("addr:district"),
        tags.get("addr:city"),
        tags.get("addr:postcode"),
    ]
    seen, cleaned = set(), []
    for part in parts:
        if part and part.lower() not in seen:
            seen.add(part.lower())
            cleaned.append(part.strip())
    return ", ".join(cleaned) or None


def element_to_listing(element: dict, city: str) -> dict | None:
    tags = element.get("tags", {})
    category = detect_category(tags)
    if not category or not tags.get("name"):
        return None
    return {
        "business_name": tags.get("name:en") or tags["name"],
        "category": category,
        "city": city,
        "address": build_address(tags),
        "phone": tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile"),
        "source": SOURCE_NAME,
    }


def scrape() -> list[dict]:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    client = PoliteClient(delay=2.0)  # Overpass is a shared free service - be gentle
    listings: list[dict] = []

    for city, bbox in config.CITIES.items():
        elements = fetch_city(client, city, bbox)
        city_rows = [row for el in elements if (row := element_to_listing(el, city))]
        log.info("[%s] %d listings", city, len(city_rows))
        listings.extend(city_rows)

    config.OSM_OUTPUT.write_text(json.dumps(listings, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("OpenStreetMap: %d listings -> %s", len(listings), config.OSM_OUTPUT)
    return listings


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    scrape()
