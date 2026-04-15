"""Test ErrorTrackerHandler: logger.error()/critical() → asyncio.Queue → ErrorRecord (board#40).

Variant C uses an asyncio.Queue. emit() enqueues, a background consumer writes to DB.
In tests, we set up the queue and drain it synchronously after each logger call.
"""

import asyncio
import logging

import pytest

import backend.main as main_module
from backend.main import _request_id_ctx
from backend.models import ErrorRecord


@pytest.fixture(autouse=True)
def _setup_error_queue():
    """Create the async error queue for the handler (normally done in lifespan)."""
    main_module._error_tracker_queue = asyncio.Queue(maxsize=1000)
    yield
    main_module._error_tracker_queue = None


def _flush_queue_to_db(db_session):
    """Drain all pending items from the error queue into the DB (sync, for tests)."""
    q = main_module._error_tracker_queue
    while not q.empty():
        data = q.get_nowait()
        if data is None:
            break
        db_session.add(ErrorRecord(
            service=data["service"],
            severity=data["severity"],
            message=data["message"],
            traceback=data["traceback"],
            request_id=data["request_id"],
        ))
        db_session.commit()


def test_logger_error_creates_record(db_session):
    """logger.error() on any non-middleware logger enqueues → ErrorRecord in DB."""
    test_logger = logging.getLogger("linza.test_module")
    test_logger.error("test error from module")
    _flush_queue_to_db(db_session)

    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.message == "test error from module"
    ).all()
    assert len(records) == 1
    assert records[0].severity == "error"
    assert records[0].service == "linza-board"


def test_middleware_logger_skipped(db_session):
    """Records from 'linza.error_reporter' must NOT be enqueued (already tracked)."""
    mw_logger = logging.getLogger("linza.error_reporter")
    mw_logger.error("middleware error — should be skipped")
    _flush_queue_to_db(db_session)

    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.message == "middleware error — should be skipped"
    ).all()
    assert len(records) == 0


def test_request_id_captured(db_session):
    """ErrorRecord.request_id is populated from ContextVar."""
    token = _request_id_ctx.set("test-req-42")
    try:
        test_logger = logging.getLogger("linza.test_reqid")
        test_logger.error("error with request id")
    finally:
        _request_id_ctx.reset(token)
    _flush_queue_to_db(db_session)

    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.message == "error with request id"
    ).all()
    assert len(records) == 1
    assert records[0].request_id == "test-req-42"


def test_critical_maps_severity(db_session):
    """logging.CRITICAL maps to severity='critical'."""
    test_logger = logging.getLogger("linza.test_critical")
    test_logger.critical("critical failure")
    _flush_queue_to_db(db_session)

    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.message == "critical failure"
    ).all()
    assert len(records) == 1
    assert records[0].severity == "critical"


def test_exc_info_traceback_captured(db_session):
    """When exc_info=True, ErrorRecord.traceback contains the exception."""
    test_logger = logging.getLogger("linza.test_exc")
    try:
        raise ValueError("test exception for traceback")
    except ValueError:
        test_logger.error("caught error", exc_info=True)
    _flush_queue_to_db(db_session)

    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.message == "caught error"
    ).all()
    assert len(records) == 1
    assert records[0].traceback is not None
    assert "ValueError" in records[0].traceback
    assert "test exception for traceback" in records[0].traceback


def test_warning_not_captured(db_session):
    """WARNING level (< ERROR) must NOT create ErrorRecord."""
    test_logger = logging.getLogger("linza.test_warning")
    test_logger.warning("just a warning")
    _flush_queue_to_db(db_session)

    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.message == "just a warning"
    ).all()
    assert len(records) == 0


def test_queue_item_structure(db_session):
    """Verify the exact structure of items put into the queue by emit()."""
    test_logger = logging.getLogger("linza.test_structure")
    token = _request_id_ctx.set("struct-123")
    try:
        test_logger.error("structure test")
    finally:
        _request_id_ctx.reset(token)

    q = main_module._error_tracker_queue
    assert not q.empty()
    data = q.get_nowait()
    assert data["service"] == "linza-board"
    assert data["severity"] == "error"
    assert data["message"] == "structure test"
    assert data["request_id"] == "struct-123"
    assert data["traceback"] is None


def test_queue_not_available_before_lifespan(db_session):
    """When queue is None (pre-lifespan), emit() silently skips."""
    old_queue = main_module._error_tracker_queue
    main_module._error_tracker_queue = None
    try:
        test_logger = logging.getLogger("linza.test_no_queue")
        # Should not raise
        test_logger.error("no queue available")
    finally:
        main_module._error_tracker_queue = old_queue

    # Queue was None, so nothing enqueued — nothing in DB
    _flush_queue_to_db(db_session)
    records = db_session.query(ErrorRecord).filter(
        ErrorRecord.message == "no queue available"
    ).all()
    assert len(records) == 0
