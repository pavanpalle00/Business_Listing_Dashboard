"""Run from the project root:  python -m pytest scraper/tests"""
import pytest

from scraper.cleaner import clean, clean_text, normalise_city, normalise_phone
from scraper.osm_scraper import build_address, element_to_listing
from scraper.wikipedia_scraper import display_name, parse_infobox


@pytest.mark.parametrize("raw, expected", [
    ("+91 80 2222 3333", "+918022223333"),
    ("080-22223333", "+918022223333"),
    ("098450 12345; 9845012346", "+919845012345"),
    ("9845012345", "+919845012345"),
    ("+91-98450-12345", "+919845012345"),
    ("1800 102 1234", "18001021234"),
    ("12345", None),
    ("", None),
    (None, None),
])
def test_normalise_phone(raw, expected):
    assert normalise_phone(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("Bangalore", "Bengaluru"),
    ("  bombay ", "Mumbai"),
    ("New Delhi", "Delhi"),
    ("navi mumbai", "Navi Mumbai"),
])
def test_normalise_city(raw, expected):
    assert normalise_city(raw) == expected


def test_clean_text_removes_noise():
    assert clean_text("  Wadala , Mumbai ,  India[3] ") == "Wadala, Mumbai, India"
    assert clean_text("Law College Rd, Pune,, Deccan") == "Law College Rd, Pune, Deccan"
    assert clean_text("   ") is None


def test_clean_rejects_invalid_and_duplicates():
    rows = [
        {"business_name": "Cafe X", "category": "Cafe", "city": "Bangalore", "address": "1 MG Road", "source": "OSM"},
        {"business_name": "cafe  x", "category": "Cafe", "city": "Bengaluru", "address": "1, MG Road", "source": "OSM"},
        {"business_name": "", "category": "Cafe", "city": "Pune", "source": "OSM"},
    ]
    result, stats = clean(rows)
    assert len(result) == 1
    assert result[0]["city"] == "Bengaluru"
    assert stats["removed_duplicates"] == 1 and stats["rejected_invalid"] == 1


def test_osm_element_to_listing():
    element = {"tags": {
        "amenity": "pharmacy", "name": "Apollo Pharmacy", "phone": "+91 80 1234 5678",
        "addr:housenumber": "12", "addr:street": "100 Feet Road", "addr:postcode": "560038",
    }}
    listing = element_to_listing(element, "Bengaluru")
    assert listing == {
        "business_name": "Apollo Pharmacy", "category": "Pharmacy", "city": "Bengaluru",
        "address": "12, 100 Feet Road, 560038", "phone": "+91 80 1234 5678", "source": "OpenStreetMap",
    }


def test_build_address_skips_repeated_parts():
    assert build_address({"addr:street": "MG Road", "addr:suburb": "Pune", "addr:city": "pune"}) == "MG Road, Pune"


def test_parse_infobox_and_display_name():
    html = """<table class="infobox"><tr><th>Location</th><td>Adyar<sup>[1]</sup>, Chennai</td></tr>
              <tr><th>Phone</th><td>044 2222 3333</td></tr></table>"""
    assert parse_infobox(html) == {"location": "Adyar, Chennai", "phone": "044 2222 3333"}
    assert display_name("Apollo Hospital (Chennai)") == "Apollo Hospital"
