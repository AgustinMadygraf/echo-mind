import json
import logging
from datetime import datetime, timezone
from typing import Any

from src.application.gateways.logger_gateway import LoggerGateway


class _Redactor:
    def __init__(self, secrets: list[str]) -> None:
        self._placeholders = [s for s in secrets if s]

    def redact(self, text: str) -> str:
        for secret in self._placeholders:
            if secret in text:
                text = text.replace(secret, "***REDACTED***")
        return text


class RedactingFilter(logging.Filter):
    """Redact any occurrence of the provided secrets in log records."""

    _PLACEHOLDER = "***REDACTED***"

    def __init__(self, secrets: list[str]) -> None:
        super().__init__()
        self._redactor = _Redactor(secrets)

    def filter(self, record: logging.LogRecord) -> bool:
        message = self._redactor.redact(record.getMessage())
        record.msg = message
        record.args = ()
        data = getattr(record, "data", None)
        if data:
            record.data = self._redactor.redact(data)
        return True


class StructuredLoggerAdapter(LoggerGateway):
    """Structured, secrets-sanitized logger backed by the stdlib `logging`."""

    def __init__(
        self,
        name: str = "echo-mind",
        level: int = logging.INFO,
        secrets: list[str] | None = None,
        handler: logging.Handler | None = None,
    ) -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.propagate = False

        if handler is None:
            handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.addFilter(RedactingFilter(secrets or []))
        handler.setFormatter(_JsonFormatter())
        self._logger.addHandler(handler)

    def _emit(self, level: str, msg: str, **kwargs: Any) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "msg": msg,
        }
        record.update(kwargs)
        getattr(self._logger, level.lower())(msg, extra={"data": json.dumps(record)})

    def info(self, msg: str, **kwargs: Any) -> None:
        self._emit("info", msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._emit("error", msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._emit("warning", msg, **kwargs)


class _JsonFormatter(logging.Formatter):
    """Output the record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(
            record.created, tz=timezone.utc
        ).isoformat()
        entry = {
            "ts": ts,
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        data = getattr(record, "data", None)
        if data:
            entry["data"] = data
        return json.dumps(entry, ensure_ascii=False)
