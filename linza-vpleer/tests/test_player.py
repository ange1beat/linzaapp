"""Тесты эндпоинтов player."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


MOCK_FILES = {
    "files": [
        {"name": "video1.mp4", "size": 10485760, "last_modified": "2025-01-01"},
        {"name": "тест видео.mkv", "size": 5242880, "last_modified": "2025-02-01"},
    ]
}

# Paths to static assets for content verification
_STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"
_PLAYER_CSS = (_STATIC_DIR / "css" / "player.css").read_text()
_TOKENS_CSS = (_STATIC_DIR / "css" / "tokens.css").read_text()
_INDEX_CSS = (_STATIC_DIR / "css" / "index.css").read_text()
_PLAYER_JS = (_STATIC_DIR / "js" / "player.js").read_text()
_THEME_JS = (_STATIC_DIR / "js" / "theme.js").read_text()


def _mock_storage_response(data=None, status_code=200):
    """Create a mock httpx.Response for storage service."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = data or MOCK_FILES
    resp.raise_for_status = MagicMock()
    return resp


@pytest.fixture
def _patch_storage():
    """Patch httpx.AsyncClient for storage calls in player module."""
    mock_response = _mock_storage_response()
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.routes.player.httpx.AsyncClient", return_value=mock_client):
        yield mock_client


def test_files_endpoint(client, _patch_storage):
    """GET /api/vpleer/files возвращает список файлов из storage."""
    resp = client.get("/api/vpleer/files")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "video1.mp4"
    assert data[1]["name"] == "тест видео.mkv"


def test_player_page_returns_html(client, _patch_storage):
    """GET /api/vpleer/player/{filename} возвращает HTML-страницу плеера."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    body = resp.text

    # Проверяем ключевые элементы HTML
    assert "<!DOCTYPE html>" in body
    assert "Linza VPleer" in body
    assert "<video" in body
    assert "video1.mp4" in body


def test_player_page_uses_json_dumps_for_js(client, _patch_storage):
    """Filename в JS-контексте экранирован через json.dumps (CLAUDE.md rule)."""
    resp = client.get("/api/vpleer/player/test%22file.mp4")
    body = resp.text
    # json.dumps produces: "test\"file.mp4" — with escaped quote
    js_escaped = json.dumps('test"file.mp4')
    assert f"const filename = {js_escaped}" in body


def test_player_page_url_encoding(client, _patch_storage):
    """URL в src использует quote(safe='/') для поддиректорий."""
    resp = client.get("/api/vpleer/player/folder/sub/video.mp4")
    body = resp.text
    # URL path should preserve slashes
    assert "/api/vpleer/stream/folder/sub/video.mp4" in body


def test_player_page_html_escape_in_title(client, _patch_storage):
    """Filename в HTML-контексте экранирован через html.escape."""
    resp = client.get("/api/vpleer/player/test%3Cscript%3E.mp4")
    body = resp.text
    # html.escape should convert < to &lt;
    assert "<script>" not in body.split("<title>")[1].split("</title>")[0]
    assert "&lt;script&gt;" in body or "test&lt;script&gt;.mp4" in body


def test_player_index_returns_file_list(client, _patch_storage):
    """GET /api/vpleer/player возвращает HTML-список файлов."""
    resp = client.get("/api/vpleer/player")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    body = resp.text
    assert "video1.mp4" in body
    assert "Linza VPleer" in body


def test_player_page_has_detections_panel(client, _patch_storage):
    """Страница плеера содержит панель нарушений."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert 'id="detectionsPanel"' in body
    assert 'id="detectionList"' in body
    assert "Нарушения" in body


def test_player_page_embed_detect_flow_no_json_modal(client, _patch_storage):
    """Ручная загрузка JSON убрана — разметка из Linza через postMessage."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert 'id="modalOverlay"' not in body
    assert "linza-detections" in body
    assert "data-theme" in body


def test_player_page_has_nav_buttons(client, _patch_storage):
    """Страница плеера содержит кнопки Prev/Next навигации."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert 'id="btnPrev"' in body
    assert 'id="btnNext"' in body
    assert 'id="navPosition"' in body


def test_player_page_has_fragment_indicator(client, _patch_storage):
    """Страница плеера содержит индикатор режима фрагмента."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert 'id="fragmentIndicator"' in body
    assert "stopFragment" in body
    # playFragment is in external JS
    assert "playFragment" in _PLAYER_JS


def test_player_page_has_two_column_layout(client, _patch_storage):
    """Страница плеера использует двухколоночную раскладку."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert "page-layout" in body
    assert "detections-panel" in body
    assert "grid-template-columns" in _PLAYER_CSS


def test_player_page_has_hls_js(client, _patch_storage):
    """Страница плеера подключает hls.js CDN."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert "hls.js" in body
    assert "Hls.isSupported()" in _PLAYER_JS


def test_player_page_has_playback_info(client, _patch_storage):
    """Страница плеера вызывает playback-info для определения стратегии."""
    assert "playback-info" in _PLAYER_JS
    assert "progressive" in _PLAYER_JS
    assert "transcode" in _PLAYER_JS


def test_player_page_has_format_badge(client, _patch_storage):
    """Страница плеера содержит бейдж формата."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert 'id="formatBadge"' in body
    assert "transcodeOverlay" in body


def test_player_page_has_design_tokens(client, _patch_storage):
    """C-1: CSS custom properties и theme toggle присутствуют."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    # data-theme attribute
    assert 'data-theme="dark"' in body
    # CSS custom properties in tokens.css
    assert '[data-theme="dark"]' in _TOKENS_CSS or ':root' in _TOKENS_CSS
    assert '[data-theme="light"]' in _TOKENS_CSS
    assert "--bg-primary" in _TOKENS_CSS
    assert "--text-primary" in _TOKENS_CSS
    # CSS uses var() tokens
    assert "var(--bg-primary)" in _TOKENS_CSS or "var(--bg-primary)" in _PLAYER_CSS
    assert "var(--text-accent)" in _PLAYER_CSS
    assert "var(--border)" in _PLAYER_CSS
    # Theme toggle button in HTML
    assert 'id="themeToggle"' in body
    assert "toggleTheme" in body
    # Theme JS (localStorage)
    assert "linza-theme" in _THEME_JS
    assert "initTheme" in _THEME_JS


def test_player_index_has_design_tokens(client, _patch_storage):
    """C-1: Страница списка файлов также использует дизайн-токены."""
    resp = client.get("/api/vpleer/player")
    body = resp.text
    assert 'data-theme="dark"' in body
    # Tokens are in external CSS file
    assert '[data-theme="light"]' in _TOKENS_CSS
    assert 'id="themeToggle"' in body
    assert "toggleTheme" in body


def test_player_page_has_dual_track_timeline(client, _patch_storage):
    """C-2: Двойная дорожка таймлайна (video + audio)."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    # Two timeline tracks in HTML
    assert 'id="trackVideo"' in body
    assert 'id="trackAudio"' in body
    assert 'data-source="video"' in body
    assert 'data-source="audio"' in body
    # Track CSS
    assert "timeline-track" in body or "timeline-track" in _PLAYER_CSS
    # JS handles source field
    assert "m.source" in _PLAYER_JS
    # Source icon in detection panel
    assert "det-source" in _PLAYER_JS or "det-source" in _PLAYER_CSS
    assert "fromCodePoint" in _PLAYER_JS


def test_player_page_has_multiclass_grouping(client, _patch_storage):
    """C-4: Группировка перекрытий и групповые карточки."""
    # Grouping function in JS
    assert "groupByOverlap" in _PLAYER_JS
    assert "groupsData" in _PLAYER_JS
    # Grouped card rendering
    assert "group-card" in _PLAYER_JS or "group-card" in _PLAYER_CSS
    assert "group-count" in _PLAYER_JS or "group-count" in _PLAYER_CSS
    # Group-based fragment playback
    assert "playGroupFragment" in _PLAYER_JS
    # Navigation by groups
    assert "groupsData.length" in _PLAYER_JS


def test_player_page_has_review_feedback(client, _patch_storage):
    """C-5: Механизм обратной связи (confirm/reject/reclassify) с SVG-иконками."""
    # Feedback CSS tokens
    assert "--feedback-confirm" in _TOKENS_CSS
    assert "--feedback-reject" in _TOKENS_CSS
    assert "--feedback-reclass" in _TOKENS_CSS
    # SVG icon system
    assert "const SVG" in _PLAYER_JS
    assert "SVG.check" in _PLAYER_JS
    assert "viewBox" in _PLAYER_JS
    # Review state classes
    assert "review-confirmed" in _PLAYER_JS or "review-confirmed" in _PLAYER_CSS
    assert "review-rejected" in _PLAYER_JS or "review-rejected" in _PLAYER_CSS
    # Review buttons with data-det-id
    assert "buildReviewButtons" in _PLAYER_JS
    assert "data-det-id" in _PLAYER_JS
    # JS functions
    assert "setReview" in _PLAYER_JS
    assert "applyReviewStates" in _PLAYER_JS
    assert "getReviewStore" in _PLAYER_JS
    # Reclassification
    assert "showReclass" in _PLAYER_JS
    assert "SUBCLASSES" in _PLAYER_JS
    # Batch confirm
    assert "confirmAllVisible" in _PLAYER_JS
    # localStorage persistence
    assert "linza-reviews" in _PLAYER_JS
    # Keyboard shortcuts
    assert "ids.forEach" in _PLAYER_JS


def test_player_page_has_filter_panel(client, _patch_storage):
    """C-6: Панель фильтров с чипами, слайдером и сортировкой."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    # Filter panel structure in HTML
    assert 'id="filterPanel"' in body
    assert 'id="filterBody"' in body
    assert 'id="filterToggle"' in body
    assert 'id="filterCategory"' in body
    assert 'id="filterSource"' in body
    assert 'id="filterStatus"' in body
    assert 'id="confSlider"' in body
    assert 'id="sortSelect"' in body
    # JS functions
    assert "applyFilters" in _PLAYER_JS
    assert "buildFilterChips" in _PLAYER_JS
    assert "resetFilters" in _PLAYER_JS
    assert "resortAndRender" in _PLAYER_JS
    # CSS
    assert "filter-chip" in _PLAYER_CSS
    assert "filtered-out" in _PLAYER_CSS


def test_player_page_has_stat_bar(client, _patch_storage):
    """C-7: Сводка-статбар с counts по категориям и статусам."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert 'id="statBar"' in body
    assert "updateStatBar" in _PLAYER_JS
    assert "stat-bar" in _PLAYER_CSS
    assert "stat-item" in _PLAYER_CSS or "stat-item" in _PLAYER_JS
    assert "stat-dot" in _PLAYER_JS
    assert "data-stat-filter" in _PLAYER_JS


def test_player_page_no_json_export_ui(client, _patch_storage):
    """Экспорт/загрузка JSON в плеере убраны — рецензия локально, PDF из Linza."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert 'id="btnExport"' not in body
    assert 'id="panelFooter"' not in body
    assert "exportReviewJson" not in body
    assert 'id="btnLoadDetections"' not in body
    assert "beforeunload" in _PLAYER_JS


def test_player_page_links_static_assets(client, _patch_storage):
    """Страница подключает CSS и JS как внешние файлы."""
    resp = client.get("/api/vpleer/player/video1.mp4")
    body = resp.text
    assert "/api/vpleer/static/css/tokens.css" in body
    assert "/api/vpleer/static/css/player.css" in body
    assert "/api/vpleer/static/js/theme.js" in body
    assert "/api/vpleer/static/js/player.js" in body


def test_player_index_links_static_assets(client, _patch_storage):
    """Страница списка файлов подключает CSS и JS как внешние файлы."""
    resp = client.get("/api/vpleer/player")
    body = resp.text
    assert "/api/vpleer/static/css/tokens.css" in body
    assert "/api/vpleer/static/css/index.css" in body
    assert "/api/vpleer/static/js/theme.js" in body
