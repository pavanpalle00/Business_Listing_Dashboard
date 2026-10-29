from conftest import SAMPLE, make_listing


def seed(client, rows=SAMPLE):
    response = client.post("/api/listings/bulk", json={"listings": rows})
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------------- bulk insert
def test_bulk_insert_inserts_all_rows(client):
    assert seed(client) == {"received": 4, "inserted": 4, "duplicates_skipped": 0}


def test_bulk_insert_is_idempotent(client):
    seed(client)
    assert seed(client) == {"received": 4, "inserted": 0, "duplicates_skipped": 4}


def test_duplicates_inside_one_request_are_skipped(client):
    rows = [make_listing(), make_listing(business_name="  TEST cafe ")]  # same after normalising
    assert seed(client, rows) == {"received": 2, "inserted": 1, "duplicates_skipped": 1}


def test_bulk_insert_rejects_invalid_rows(client):
    bad = [make_listing(), make_listing(business_name="")]
    response = client.post("/api/listings/bulk", json={"listings": bad})
    assert response.status_code == 422
    # all-or-nothing: the valid row was not written either
    assert client.get("/api/dashboard/summary").json()["total_listings"] == 0


def test_bulk_insert_rejects_empty_list(client):
    assert client.post("/api/listings/bulk", json={"listings": []}).status_code == 422


def test_blank_optional_fields_become_null(client):
    seed(client, [make_listing(phone="   ", address="")])
    item = client.get("/api/listings").json()["items"][0]
    assert item["phone"] is None and item["address"] is None


# ------------------------------------------------------------------ dashboard
def test_city_count(client):
    seed(client)
    body = client.get("/api/dashboard/city-count").json()
    assert body["dimension"] == "city"
    assert body["total"] == 4
    assert body["items"] == [{"label": "Bengaluru", "count": 2}, {"label": "Mumbai", "count": 2}]


def test_category_count_sorted_by_count_desc(client):
    seed(client)
    items = client.get("/api/dashboard/category-count").json()["items"]
    assert items[0] == {"label": "Cafe", "count": 2}
    assert [i["count"] for i in items] == sorted((i["count"] for i in items), reverse=True)


def test_source_count(client):
    seed(client)
    items = client.get("/api/dashboard/source-count").json()["items"]
    assert items == [{"label": "OpenStreetMap", "count": 3}, {"label": "Wikipedia", "count": 1}]


def test_count_filters_and_limit(client):
    seed(client)
    mumbai = client.get("/api/dashboard/category-count", params={"city": "Mumbai"}).json()
    assert mumbai["total"] == 2
    top1 = client.get("/api/dashboard/category-count", params={"limit": 1}).json()
    assert len(top1["items"]) == 1 and top1["total"] == 4


def test_summary(client):
    seed(client)
    assert client.get("/api/dashboard/summary").json() == {
        "total_listings": 4, "cities": 2, "categories": 3, "sources": 2, "with_phone": 3,
    }


def test_empty_database_returns_zeroes(client):
    assert client.get("/api/dashboard/city-count").json() == {"dimension": "city", "total": 0, "items": []}


# ------------------------------------------------------------------- listings
def test_list_listings_pagination_and_search(client):
    seed(client)
    page = client.get("/api/listings", params={"page_size": 2, "page": 2}).json()
    assert page["total"] == 4 and page["pages"] == 2 and len(page["items"]) == 2

    found = client.get("/api/listings", params={"search": "hosp"}).json()
    assert [i["business_name"] for i in found["items"]] == ["City Hospital"]


def test_page_size_is_capped(client):
    assert client.get("/api/listings", params={"page_size": 1000}).status_code == 422


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok", "database": "connected"}
