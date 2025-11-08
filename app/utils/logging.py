"""
Logging configuration with optional JSON output.
"""
import logging
import sys
import json
import os
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
            "service": "clankerbot",
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "path"):
            log_obj["path"] = record.path
        if hasattr(record, "status"):
            log_obj["status"] = record.status
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms

        # Add exception info if present
        if record.exc_info:
            log_obj["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure logging with optional JSON format.
    Set LOG_JSON=true in env to enable JSON logging.
    """
    use_json = os.getenv("LOG_JSON", "").lower() in ("true", "1", "yes")

    handler = logging.StreamHandler(sys.stdout)

    if use_json:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )

    logging.basicConfig(
        level=level,
        handlers=[handler],
    )
