"""Тесты утилит модуля stream."""

from app.routes.stream import CONTENT_TYPES, _safe_content_disposition


class TestSafeContentDisposition:
    """Тесты RFC 5987 Content-Disposition."""

    def test_ascii_filename(self):
        result = _safe_content_disposition("video.mp4")
        assert result == "inline; filename*=UTF-8''video.mp4"

    def test_unicode_filename(self):
        result = _safe_content_disposition("видео файл.mp4")
        assert "UTF-8''" in result
        assert "inline" in result
        # Кириллица должна быть percent-encoded
        assert "видео" not in result
        assert "%D0%B2" in result  # 'в' encoded

    def test_disposition_attachment(self):
        result = _safe_content_disposition("file.mp4", disposition="attachment")
        assert result.startswith("attachment;")

    def test_special_characters(self):
        """Спецсимволы в имени файла корректно кодируются."""
        result = _safe_content_disposition('file "quotes" & spaces.mp4')
        assert "UTF-8''" in result
        # Quotes and spaces should be encoded
        assert '"' not in result.split("''")[1]
        assert " " not in result.split("''")[1]

    def test_subdirectory_path(self):
        """Слэши в пути кодируются (safe='')."""
        result = _safe_content_disposition("folder/subfolder/video.mp4")
        assert "%2F" in result or "%2f" in result


class TestContentTypes:
    """Тесты маппинга расширений к MIME-типам."""

    def test_mp4(self):
        assert CONTENT_TYPES[".mp4"] == "video/mp4"

    def test_avi(self):
        assert CONTENT_TYPES[".avi"] == "video/x-msvideo"

    def test_mkv(self):
        assert CONTENT_TYPES[".mkv"] == "video/x-matroska"

    def test_mov(self):
        assert CONTENT_TYPES[".mov"] == "video/quicktime"

    def test_webm(self):
        assert CONTENT_TYPES[".webm"] == "video/webm"

    def test_m4v(self):
        assert CONTENT_TYPES[".m4v"] == "video/mp4"

    def test_mpeg(self):
        assert CONTENT_TYPES[".mpeg"] == "video/mpeg"

    def test_mpg(self):
        assert CONTENT_TYPES[".mpg"] == "video/mpeg"

    def test_mxf(self):
        assert CONTENT_TYPES[".mxf"] == "application/mxf"

    def test_hevc(self):
        assert CONTENT_TYPES[".hevc"] == "video/mp4"

    def test_all_expected_extensions_present(self):
        expected = {
            ".mp4", ".m4v", ".avi", ".mkv", ".mov", ".webm",
            ".mpeg", ".mpg", ".mxf", ".hevc",
        }
        assert set(CONTENT_TYPES.keys()) == expected
