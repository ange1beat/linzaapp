"""Тесты для таймаутов ffmpeg операций."""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def temp_dir(tmp_path):
    """Переопределить TEMP_DIR для тестов."""
    with patch("app.services.ffmpeg.TEMP_DIR", str(tmp_path)):
        yield tmp_path


def _make_proc_mock(returncode=0, stdout=b"", stderr=b""):
    """Создать мок subprocess, который завершается нормально."""
    proc = AsyncMock()
    proc.communicate = AsyncMock(return_value=(stdout, stderr))
    proc.returncode = returncode
    proc.kill = MagicMock()
    proc.wait = AsyncMock()
    return proc


def _make_hanging_proc_mock():
    """Создать мок subprocess, который зависает (для тестирования таймаута)."""
    proc = AsyncMock()

    async def hang():
        await asyncio.sleep(9999)

    proc.communicate = AsyncMock(side_effect=hang)
    proc.returncode = None
    proc.kill = MagicMock()
    proc.wait = AsyncMock()
    return proc


def test_extract_thumbnail_timeout(temp_dir):
    """Thumbnail: при таймауте процесс убивается, temp-файл удаляется."""
    hanging_proc = _make_hanging_proc_mock()

    with patch("app.services.ffmpeg.FFMPEG_THUMBNAIL_TIMEOUT", 0.1), \
         patch("asyncio.create_subprocess_exec", return_value=hanging_proc):

        from app.services.ffmpeg import extract_thumbnail

        with pytest.raises(RuntimeError, match="thumbnail timeout"):
            asyncio.run(extract_thumbnail("/fake/video.mp4", time_sec=1.0))

        hanging_proc.kill.assert_called_once()


def test_extract_thumbnail_success(temp_dir):
    """Thumbnail: нормальная работа без таймаута."""
    ok_proc = _make_proc_mock(returncode=0)

    with patch("asyncio.create_subprocess_exec", return_value=ok_proc):
        from app.services.ffmpeg import extract_thumbnail

        result = asyncio.run(extract_thumbnail("/fake/video.mp4", time_sec=1.0))
        assert result.endswith(".jpg")
        ok_proc.kill.assert_not_called()


def test_extract_fragment_timeout(temp_dir):
    """Fragment: при таймауте процесс убивается, temp-файл удаляется."""
    hanging_proc = _make_hanging_proc_mock()

    with patch("app.services.ffmpeg.FFMPEG_FRAGMENT_TIMEOUT", 0.1), \
         patch("asyncio.create_subprocess_exec", return_value=hanging_proc):

        from app.services.ffmpeg import extract_fragment

        with pytest.raises(RuntimeError, match="fragment timeout"):
            asyncio.run(extract_fragment("/fake/video.mp4", 0.0, 10.0))

        hanging_proc.kill.assert_called_once()


def test_extract_fragment_success(temp_dir):
    """Fragment: нормальная работа без таймаута."""
    ok_proc = _make_proc_mock(returncode=0)

    with patch("asyncio.create_subprocess_exec", return_value=ok_proc):
        from app.services.ffmpeg import extract_fragment

        result = asyncio.run(extract_fragment("/fake/video.mp4", 0.0, 10.0))
        assert result.endswith(".mp4")
        ok_proc.kill.assert_not_called()


def test_generate_hls_timeout(temp_dir):
    """HLS: при таймауте процесс убивается, hls_dir удаляется."""
    hanging_proc = _make_hanging_proc_mock()

    hls_dir = temp_dir / "hls" / "test_video.mp4"

    with patch("app.services.ffmpeg.FFMPEG_HLS_TIMEOUT", 0.1), \
         patch("asyncio.create_subprocess_exec", return_value=hanging_proc):

        from app.services.ffmpeg import generate_hls

        with pytest.raises(RuntimeError, match="HLS timeout"):
            asyncio.run(generate_hls("http://storage/test_video.mp4", "test_video.mp4"))

        hanging_proc.kill.assert_called_once()
        assert not hls_dir.exists()


def test_generate_hls_success(temp_dir):
    """HLS: нормальная работа без таймаута."""
    ok_proc = _make_proc_mock(returncode=0)

    with patch("asyncio.create_subprocess_exec", return_value=ok_proc):
        from app.services.ffmpeg import generate_hls

        result = asyncio.run(
            generate_hls("http://storage/test.mp4", "test.mp4", codec="h264")
        )
        assert result.endswith("playlist.m3u8")
        ok_proc.kill.assert_not_called()


def test_thumbnail_timeout_cleans_partial_file(temp_dir):
    """При таймауте thumbnail удаляет частично созданный файл."""
    hanging_proc = _make_hanging_proc_mock()

    partial_file = temp_dir / "partial.jpg"
    partial_file.write_bytes(b"partial data")

    with patch("app.services.ffmpeg.FFMPEG_THUMBNAIL_TIMEOUT", 0.1), \
         patch("asyncio.create_subprocess_exec", return_value=hanging_proc), \
         patch("tempfile.mktemp", return_value=str(partial_file)):

        from app.services.ffmpeg import extract_thumbnail

        with pytest.raises(RuntimeError, match="thumbnail timeout"):
            asyncio.run(extract_thumbnail("/fake/video.mp4"))

        assert not partial_file.exists()
