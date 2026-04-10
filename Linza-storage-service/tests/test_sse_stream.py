"""Tests for GET /api/files/progress/{task_id} — SSE progress stream."""

import json

from app.tasks import set_task


def _parse_sse(text: str) -> list[dict]:
    """Extract JSON payloads from SSE 'data:' lines."""
    events = []
    for line in text.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line[len("data: "):]))
    return events


class TestSSEProgressStream:
    """SSE endpoint emits one event per poll; breaks on terminal state."""

    def test_unknown_task_returns_not_found_event(self, client):
        resp = client.get("/api/files/progress/nonexistent-id")
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        events = _parse_sse(resp.text)
        assert len(events) == 1
        assert events[0]["status"] == "not_found"

    def test_completed_task_emits_single_event_and_stops(self, client):
        set_task("done-task", {
            "status": "completed", "progress": 1000,
            "total": 1000, "filename": "uploads/done.mp4",
        })
        resp = client.get("/api/files/progress/done-task")
        events = _parse_sse(resp.text)
        assert len(events) == 1
        assert events[0]["status"] == "completed"
        assert events[0]["progress"] == 1000

    def test_error_task_emits_single_event_and_stops(self, client):
        set_task("err-task", {
            "status": "error", "error": "upload failed",
            "progress": 0, "total": 500, "filename": "uploads/fail.mp4",
        })
        resp = client.get("/api/files/progress/err-task")
        events = _parse_sse(resp.text)
        assert len(events) == 1
        assert events[0]["status"] == "error"
        assert "upload failed" in events[0]["error"]

    def test_response_has_sse_headers(self, client):
        resp = client.get("/api/files/progress/any-id")
        assert resp.headers.get("cache-control") == "no-cache"
        assert resp.headers.get("x-accel-buffering") == "no"

    def test_sse_payload_contains_task_fields(self, client):
        """SSE event data is a valid JSON object with expected task fields."""
        set_task("fields-task", {
            "status": "completed", "progress": 200,
            "total": 200, "filename": "uploads/clip.mp4",
        })
        resp = client.get("/api/files/progress/fields-task")
        events = _parse_sse(resp.text)
        assert len(events) == 1
        ev = events[0]
        assert "status" in ev
        assert "progress" in ev
        assert "filename" in ev
