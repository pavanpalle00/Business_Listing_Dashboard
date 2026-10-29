"""Central configuration for the scraping pipeline.

Everything that decides *what* gets scraped lives here, so the scrapers
themselves only contain *how* to scrape.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRAPER_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRAPER_DIR / "data"
RAW_DIR = DATA_DIR / "raw"  # cached API responses (git-ignored)

OSM_OUTPUT = DATA_DIR / "osm_listings.json"
WIKI_OUTPUT = DATA_DIR / "wikipedia_listings.json"
CLEAN_JSON = DATA_DIR / "listings_clean.json"
CLEAN_CSV = DATA_DIR / "listings_clean.csv"

# ---------------------------------------------------------------------------
# HTTP etiquette
# ---------------------------------------------------------------------------
# Both OpenStreetMap and Wikimedia ask clients to identify themselves.
USER_AGENT = (
    "BusinessListingsDashboard/1.0 "
    "(Python internship assignment; contact: pavanpalle00@gmail.com)"
)
REQUEST_TIMEOUT = 90          # seconds
REQUEST_DELAY = 1.0           # seconds to wait between requests (politeness)
MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# Source 1: OpenStreetMap via the Overpass API
# ---------------------------------------------------------------------------
# Public Overpass instances, tried in order until one answers.
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# Bounding box per city: (south, west, north, east)
CITIES = {
    "Bengaluru": (12.85, 77.50, 13.10, 77.75),
    "Mumbai": (18.90, 72.80, 19.25, 72.98),
    "Delhi": (28.50, 77.05, 28.75, 77.30),
    "Chennai": (12.95, 80.15, 13.15, 80.30),
    "Hyderabad": (17.30, 78.35, 17.50, 78.55),
    "Kolkata": (22.48, 88.28, 22.65, 88.42),
    "Pune": (18.45, 73.75, 18.62, 73.95),
    "Ahmedabad": (22.95, 72.50, 23.10, 72.65),
}

# Dashboard category  ->  OSM tag (key, value)
OSM_CATEGORIES = {
    "Restaurant": ("amenity", "restaurant"),
    "Cafe": ("amenity", "cafe"),
    "Hospital": ("amenity", "hospital"),
    "Clinic": ("amenity", "clinic"),
    "Pharmacy": ("amenity", "pharmacy"),
    "School": ("amenity", "school"),
    "College": ("amenity", "college"),
    "Bank": ("amenity", "bank"),
    "Gym": ("leisure", "fitness_centre"),
    "Hotel": ("tourism", "hotel"),
    "Supermarket": ("shop", "supermarket"),
    "Salon": ("shop", "hairdresser"),
}

# Max listings per (city, category) - keeps the dataset balanced so one
# huge category (e.g. restaurants in Mumbai) does not dominate the charts.
OSM_LIMIT_PER_CATEGORY = 30

# ---------------------------------------------------------------------------
# Source 2: Wikipedia (MediaWiki API + BeautifulSoup HTML parsing)
# ---------------------------------------------------------------------------
WIKI_API = "https://en.wikipedia.org/w/api.php"

# (dashboard category, city, Wikipedia category title)
WIKI_CATEGORIES = [
    ("Hospital", "Mumbai", "Hospitals in Mumbai"),
    ("Hospital", "Chennai", "Hospitals in Chennai"),
    ("Hospital", "Hyderabad", "Hospitals in Hyderabad, India"),
    ("Hospital", "Delhi", "Hospitals in Delhi"),
    ("Hospital", "Kolkata", "Hospitals in Kolkata"),
    ("Hospital", "Pune", "Hospitals in Pune"),
    ("Hospital", "Bengaluru", "Hospitals in Bengaluru"),
    ("Hotel", "Chennai", "Hotels in Chennai"),
    ("Hotel", "Delhi", "Hotels in Delhi"),
    ("Hotel", "Kolkata", "Hotels in Kolkata"),
    ("Hotel", "Bengaluru", "Hotels in Bengaluru"),
    ("Restaurant", "Mumbai", "Restaurants in Mumbai"),
    ("Restaurant", "Kolkata", "Restaurants in Kolkata"),
    ("Restaurant", "Delhi", "Restaurants in Delhi"),
    ("Restaurant", "Chennai", "Restaurants in Chennai"),
    ("Restaurant", "Bengaluru", "Restaurants in Bengaluru"),
    ("Shopping Mall", "Mumbai", "Shopping malls in Mumbai"),
    ("Shopping Mall", "Chennai", "Shopping malls in Chennai"),
    ("Shopping Mall", "Hyderabad", "Shopping malls in Hyderabad, India"),
    ("Shopping Mall", "Delhi", "Shopping malls in Delhi"),
    ("Shopping Mall", "Kolkata", "Shopping malls in Kolkata"),
    ("Shopping Mall", "Bengaluru", "Shopping malls in Bengaluru"),
    ("School", "Mumbai", "Schools in Mumbai"),
    ("School", "Chennai", "Schools in Chennai"),
    ("School", "Kolkata", "Schools in Kolkata"),
    ("School", "Hyderabad", "Schools in Hyderabad, India"),
    ("School", "Delhi", "Schools in Delhi"),
    ("School", "Pune", "Schools in Pune"),
    ("School", "Bengaluru", "Schools in Bengaluru"),
    ("Bank", "Mumbai", "Banks based in Mumbai"),
]

# ---------------------------------------------------------------------------
# Cleaning rules
# ---------------------------------------------------------------------------
# Alternate / historical spellings  ->  canonical city name
CITY_ALIASES = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
    "madras": "Chennai",
    "chennai": "Chennai",
    "calcutta": "Kolkata",
    "kolkata": "Kolkata",
    "new delhi": "Delhi",
    "delhi": "Delhi",
    "hyderabad": "Hyderabad",
    "secunderabad": "Hyderabad",
    "pune": "Pune",
    "poona": "Pune",
    "ahmedabad": "Ahmedabad",
}

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
API_BASE_URL = "http://localhost:8000"
UPLOAD_BATCH_SIZE = 250
