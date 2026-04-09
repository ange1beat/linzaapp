from app.db import DEFAULT_CONFIG


def test_get_classifier_returns_21_items(client):
    resp = client.get("/api/classifier/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 21
    subclasses = {item["subclass"] for item in data}
    assert subclasses == {item[0] for item in DEFAULT_CONFIG}


def test_put_updates_category(client):
    resp = client.put("/api/classifier/", json=[
        {"subclass": "NUDE", "category": "prohibited"},
    ])
    assert resp.status_code == 200
    data = resp.json()
    nude = next(item for item in data if item["subclass"] == "NUDE")
    assert nude["category"] == "prohibited"


def test_put_rejects_unknown_subclass(client):
    resp = client.put("/api/classifier/", json=[
        {"subclass": "UNKNOWN_THING", "category": "18+"},
    ])
    assert resp.status_code == 400
    assert "Unknown subclass" in resp.json()["detail"]


def test_put_rejects_invalid_category(client):
    resp = client.put("/api/classifier/", json=[
        {"subclass": "NUDE", "category": "invalid_cat"},
    ])
    assert resp.status_code == 400
    assert "Invalid category" in resp.json()["detail"]


def test_put_rejects_over_100_items(client):
    items = [{"subclass": "NUDE", "category": "18+"} for _ in range(101)]
    resp = client.put("/api/classifier/", json=items)
    assert resp.status_code == 400
    assert "Too many items" in resp.json()["detail"]


def test_reset_restores_defaults(client):
    # First change something
    client.put("/api/classifier/", json=[
        {"subclass": "NUDE", "category": "prohibited"},
    ])
    # Then reset
    resp = client.put("/api/classifier/reset")
    assert resp.status_code == 200
    data = resp.json()
    nude = next(item for item in data if item["subclass"] == "NUDE")
    assert nude["category"] == "18+"


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "analytics-service"
