"""Tests for X-Request-ID tracing."""


def test_response_has_x_request_id(client):
    resp = client.get("/health")
    assert "x-request-id" in resp.headers


def test_propagates_incoming_request_id(client):
    resp = client.get("/health", headers={"X-Request-ID": "trace-abc"})
    assert resp.headers["x-request-id"] == "trace-abc"


def test_generates_request_id_when_missing(client):
    resp = client.get("/health")
    rid = resp.headers["x-request-id"]
    assert len(rid) == 8
