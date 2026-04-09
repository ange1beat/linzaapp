"""Test uvicorn loggers are reconfigured for JSON output (board#38)."""

import logging


def test_uvicorn_loggers_propagate_after_lifespan(client):
    """Lifespan reconfigures uvicorn loggers: propagate=True, no own handlers."""
    client.get("/health")
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        assert uv_logger.propagate is True, f"{name}.propagate should be True"
        assert len(uv_logger.handlers) == 0, f"{name} should have no handlers"
