"""Test request_id appears in log records via ContextVar + Filter (board#39)."""

import logging

from app.main import RequestIDFilter, _request_id_ctx


def test_filter_injects_request_id_from_contextvar():
    token = _request_id_ctx.set("abc-123")
    try:
        filt = RequestIDFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        filt.filter(record)
        assert record.request_id == "abc-123"
    finally:
        _request_id_ctx.reset(token)


def test_filter_defaults_to_empty_string():
    filt = RequestIDFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
    filt.filter(record)
    assert record.request_id == ""
