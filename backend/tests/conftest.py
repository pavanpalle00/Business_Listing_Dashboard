"""Test fixtures.

The tests run against an in-memory SQLite database so they need no MySQL
server. The SQL issued by the API (INSERT, GROUP BY, COUNT) is standard and
behaves the same on both engines.
"""
import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"  # must be set before importing the app

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


def make_listing(**overrides) -> dict:
    listing = {
        "business_name": "Test Cafe",
        "category": "Cafe",
        "city": "Bengaluru",
        "address": "1, MG Road, Bengaluru",
        "phone": "+918000000000",
        "source": "OpenStreetMap",
    }
    listing.update(overrides)
    return listing


SAMPLE = [
    make_listing(business_name="Cafe A", address="1 Road"),
    make_listing(business_name="Cafe B", address="2 Road"),
    make_listing(business_name="City Hospital", category="Hospital", city="Mumbai", address="3 Road"),
    make_listing(business_name="Mall One", category="Shopping Mall", city="Mumbai", address=None,
                 phone=None, source="Wikipedia"),
]
