import sys
from os.path import dirname, abspath
# Hack to import shared modules from parent directory
sys.path.append(dirname(dirname(abspath(__file__))))
from unittest.mock import Mock, MagicMock
import unittest
import importer_api.api as api
import importer_api.handlers as handlers
import importer_api.crawl_handlers as crawl_handlers


class TestStaticPath(unittest.TestCase):
    def test_if_static_path_is_str(self):
        self.assertIsInstance(api.static_path, str)


class TestRoutes(unittest.TestCase):
    def test_routes_is_list(self):
        self.assertIsInstance(api.routes, list)

    def test_get_routes_returns_list(self):
        self.assertIsInstance(api.get_routes(), list)


class TestCrawlHandlersGetParseResultsHandler(unittest.TestCase):
    app_mock = api.get_application()
    request_mock = MagicMock()
    GetParseResultsHandler = crawl_handlers.GetParseResultsHandler(app_mock, request_mock)

    def test_GetParseResultsHandler_supported_methods(self):
        self.assertIsInstance(self.GetParseResultsHandler.SUPPORTED_METHODS, list)

    def test_GetParseResultsHandler_headers(self):
        self.assertIsInstance(self.GetParseResultsHandler.HEADERS, dict)

    # def test_clean_content_returns_string(self):
    #     self.assertIsInstance(self.GetParseResultsHandler.clean_content("123rfcqwfcq"), str)

    # def test_get_content_returns_binary(self):
    #     self.assertIsInstance(self.GetParseResultsHandler.get_content("https://ya.ru"), bytes)

    def test_parse_content_none_if_no_content_mapping(self):
        content = b"123"
        mapping = {}
        self.assertIsNone(self.GetParseResultsHandler.parse_field("content", content, mapping))

    def test_parse_content_none_if_param_is_string_not_bynary(self):
        content = "123"
        mapping = {}
        self.assertIsNone(self.GetParseResultsHandler.parse_field("content", content, mapping))

    def test_parse_content_none_if_mapping_is_not_dict(self):
        content = b"123"
        mapping = []
        self.assertIsNone(self.GetParseResultsHandler.parse_field("content", content, mapping))

    # def test_parse_content_none_if_content_mapping_incorrect(self):
    #     content = b"123"
    #     mapping = {"content": {"area": [{"query": "////", "method": "xpath"}], "exclude": []}}
    #     self.assertIsNone(self.GetParseResultsHandler.parse_field("content", content, mapping))

    def test_parse_title_none_if_no_title_mapping(self):
        content = b"123"
        mapping = {}
        self.assertIsNone(self.GetParseResultsHandler.parse_field("title", content, mapping))

    def test_parse_author_none_if_no_author_mapping(self):
        content = b"123"
        mapping = {}
        self.assertIsNone(self.GetParseResultsHandler.parse_field("author", content, mapping))
# if __name__=="__main__":
#     unittest.main()
