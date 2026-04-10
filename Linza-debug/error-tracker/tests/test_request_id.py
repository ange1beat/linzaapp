"""Tests for X-Request-ID tracing and request_id filter."""


def test_filter_errors_by_request_id(client):
    """POST error with request_id → GET ?request_id=... → found."""
    client.post("/api/errors/report", json={
        "service": "vpleer",
        "message": "trace test",
        "request_id": "trace-xyz",
    })
    client.post("/api/errors/report", json={
        "service": "vpleer",
        "message": "other error",
        "request_id": "other-id",
    })

    resp = client.get("/api/errors", params={"request_id": "trace-xyz"})
    data = resp.json()
    assert data["total"] == 1
    assert data["errors"][0]["request_id"] == "trace-xyz"


def test_filter_request_id_no_match(client):
    client.post("/api/errors/report", json={
        "service": "vpleer",
        "message": "err",
        "request_id": "abc",
    })
    resp = client.get("/api/errors", params={"request_id": "nonexistent"})
    assert resp.json()["total"] == 0
