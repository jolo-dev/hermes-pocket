from __future__ import annotations

import logging
from typing import Any

from pythonjsonlogger.json import JsonFormatter

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(event)s"


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(LOG_FORMAT))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def safe_log_fields(*, request_id: str, event: str, **metadata: Any) -> dict[str, Any]:
    prohibited_keys = {"body", "content", "document", "password", "query", "screen", "text"}
    if prohibited_keys.intersection(metadata):
        raise ValueError("Content-bearing fields are prohibited in service diagnostics")
    return {"request_id": request_id, "event": event, **metadata}
