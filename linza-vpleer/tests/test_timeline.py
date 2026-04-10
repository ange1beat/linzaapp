"""Тесты эндпоинта /api/vpleer/timeline."""

import json
from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest


CLASSIFIER_CONFIG = [
    {"subclass": "weapon", "category": "prohibited"},
    {"subclass": "drugs", "category": "prohibited"},
    {"subclass": "nudity", "category": "18+"},
    {"subclass": "violence", "category": "16+"},
]


def _mock_classifier_response():
    """Create a mock httpx.Response for the classifier endpoint."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.json.return_value = CLASSIFIER_CONFIG
    resp.raise_for_status = MagicMock()
    return resp


@pytest.fixture
def _patch_analytics():
    """Patch httpx.AsyncClient to return classifier config."""
    mock_response = _mock_classifier_response()
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.routes.timeline.httpx.AsyncClient", return_value=mock_client):
        yield mock_client


def test_timeline_with_valid_detections(client, _patch_analytics):
    """Timeline с валидными детекциями обогащает их категориями и цветами."""
    detections = [
        {"id": "1", "subclass": "weapon", "start_time": "00:00:05", "end_time": "00:00:10", "confidence": 0.95},
        {"id": "2", "subclass": "nudity", "start_time": "00:01:00", "end_time": "00:01:30", "confidence": 0.8},
        {"id": "3", "subclass": "unknown_class", "start_time": 120, "end_time": 130, "confidence": 0.6},
    ]
    resp = client.get(
        "/api/vpleer/timeline",
        params={"filename": "test.mp4", "detections": json.dumps(detections)},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test.mp4"
    assert len(data["markers"]) == 3

    # weapon -> prohibited -> #dc3545
    assert data["markers"][0]["category"] == "prohibited"
    assert data["markers"][0]["color"] == "#dc3545"

    # nudity -> 18+ -> #fd7e14
    assert data["markers"][1]["category"] == "18+"
    assert data["markers"][1]["color"] == "#fd7e14"

    # unknown_class -> defaults to 16+ -> #ffc107
    assert data["markers"][2]["category"] == "16+"
    assert data["markers"][2]["color"] == "#ffc107"

    assert "categories" in data

    # C-3: source field passthrough (default "both")
    assert data["markers"][0]["source"] == "both"
    assert data["markers"][1]["source"] == "both"


def test_timeline_source_field_passthrough(client, _patch_analytics):
    """C-3: source field пробрасывается из входных данных."""
    detections = [
        {"id": "1", "subclass": "weapon", "start_time": "00:00:05", "end_time": "00:00:10", "confidence": 0.9, "source": "video"},
        {"id": "2", "subclass": "nudity", "start_time": "00:01:00", "end_time": "00:01:30", "confidence": 0.8, "source": "audio"},
        {"id": "3", "subclass": "violence", "start_time": "00:02:00", "end_time": "00:02:10", "confidence": 0.7},
    ]
    resp = client.get(
        "/api/vpleer/timeline",
        params={"filename": "test.mp4", "detections": json.dumps(detections)},
    )
    assert resp.status_code == 200
    markers = resp.json()["markers"]
    assert markers[0]["source"] == "video"
    assert markers[1]["source"] == "audio"
    assert markers[2]["source"] == "both"  # default


def test_timeline_invalid_json_returns_400(client, _patch_analytics):
    """Невалидный JSON в detections возвращает 400."""
    resp = client.get(
        "/api/vpleer/timeline",
        params={"filename": "test.mp4", "detections": "not-valid-json{{{"},
    )
    assert resp.status_code == 400


def test_timeline_without_detections_returns_categories(client, _patch_analytics):
    """Без детекций возвращает пустые markers и конфигурацию классификатора."""
    resp = client.get(
        "/api/vpleer/timeline",
        params={"filename": "test.mp4"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test.mp4"
    assert data["markers"] == []
    assert "categories" in data
    assert "classifier" in data
    assert data["classifier"] == CLASSIFIER_CONFIG


def test_timeline_vaf_time_based_when_analytics_unreachable(client):
    """Docker без linza-analytics: маркеры строятся, type=audio → дорожка audio."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("no analytics"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    vaf_det = [
        {
            "subclass": "k2_2",
            "type": "audio",
            "start_time": "00:00:18",
            "end_time": "00:00:22",
            "confidence": 1.0,
        }
    ]
    with patch("app.routes.timeline.httpx.AsyncClient", return_value=mock_client):
        resp = client.post(
            "/api/vpleer/timeline",
            json={"filename": "sources/video.mp4", "detections": vaf_det},
        )
    assert resp.status_code == 200
    markers = resp.json()["markers"]
    assert len(markers) == 1
    assert markers[0]["subclass"] == "k2_2"
    assert markers[0]["source"] == "audio"
    assert markers[0]["category"] == "16+"


def test_timeline_post_large_payload(client, _patch_analytics):
    """POST /timeline принимает большое тело без query string."""
    detections = [
        {
            "id": str(i),
            "subclass": "weapon" if i % 2 == 0 else "nudity",
            "start_time": f"00:00:{i % 60:02d}.000",
            "end_time": f"00:00:{(i + 1) % 60:02d}.000",
            "confidence": 0.9,
        }
        for i in range(500)
    ]
    resp = client.post(
        "/api/vpleer/timeline",
        json={"filename": "big-report.mp4", "detections": detections},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "big-report.mp4"
    assert len(data["markers"]) == 500
    assert data["markers"][0]["category"] == "prohibited"
    assert "classifier" not in data
