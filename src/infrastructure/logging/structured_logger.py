import json
import logging
from datetime import UTC, datetime
from typing import Any, cast

from src.application.gateways.logger_gateway import LoggerGateway

_DATA_ATTR = "data"


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

    def _redact_dict(self, value: Any) -> Any:
        if isinstance(value, dict):
            result: dict[str, Any] = {}
            value_dict = cast(dict[str, Any], value)
            for item_key, item_value in value_dict.items():
                result[str(item_key)] = self._redact_dict(item_value)
            return result
        if isinstance(value, list):
            result_list: list[Any] = []
            value_list = cast(list[Any], value)
            for item in value_list:
                result_list.append(self._redact_dict(item))
            return result_list
        if isinstance(value, str):
            return self._redactor.redact(value)
        return value

    def filter(self, record: logging.LogRecord) -> bool:
        message = self._redactor.redact(record.getMessage())
        record.msg = message
        record.args = ()
        data = getattr(record, _DATA_ATTR, None)
        if isinstance(data, dict):
            record.data = self._redact_dict(data)
        return True


class _BaseFormatter(logging.Formatter):
    LEVEL_ICONS = {
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "❌",
    }


class _HumanFormatter(_BaseFormatter):
    """Column-aligned, human-friendly log lines for interactive terminals."""

    def format(self, record: logging.LogRecord) -> str:
        time_str = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        icon = self.LEVEL_ICONS.get(record.levelname, "·")
        level = record.levelname.ljust(7)
        parts = [f"{time_str} {icon} {level} {record.getMessage()}"]

        data = getattr(record, _DATA_ATTR, None)
        if isinstance(data, dict):
            data_dict = cast(dict[str, Any], data)
            pairs = "  ".join(
                f"{k}={v}"
                for k, v in data_dict.items()
                if k not in ("ts", "level", "msg")
            )
            if pairs:
                parts.append(pairs)

        return "\n".join(parts)


class _JsonFormatter(_BaseFormatter):
    """Single-line JSON output (no nested stringified fields)."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        data = getattr(record, _DATA_ATTR, None)
        if isinstance(data, dict):
            data_dict = cast(dict[str, Any], data)
            for key, value in data_dict.items():
                if key not in entry:
                    entry[key] = value
        return json.dumps(entry, ensure_ascii=False, default=str)


class StructuredLoggerAdapter(LoggerGateway):
    """Structured, secrets-sanitized logger backed by the stdlib `logging`."""

    def __init__(
        self,
        name: str = "echo-mind",
        level: int = logging.INFO,
        secrets: list[str] | None = None,
        handler: logging.Handler | None = None,
        human_readable: bool | None = None,
    ) -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.propagate = False

        if handler is None:
            handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.addFilter(RedactingFilter(secrets or []))

        if human_readable is None:
            stream: Any = getattr(handler, "stream", None) if hasattr(handler, "stream") else None
            isatty = getattr(stream, "isatty", None)
            human_readable = bool(callable(isatty) and isatty())
        formatter: logging.Formatter = (
            _HumanFormatter() if human_readable else _JsonFormatter()
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def _emit(self, level: str, msg: str, **kwargs: Any) -> None:
        data = {
            "ts": datetime.now(UTC).isoformat(),
            "level": level.upper(),
            "msg": msg,
        }
        data.update(kwargs)
        getattr(self._logger, level.lower())(msg, extra={_DATA_ATTR: data})

    def info(self, msg: str, **kwargs: Any) -> None:
        self._emit("info", msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._emit("error", msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._emit("warning", msg, **kwargs)
