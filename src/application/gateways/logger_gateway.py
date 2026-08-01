from abc import ABC, abstractmethod
from typing import Any


class LoggerGateway(ABC):
    @abstractmethod
    def info(self, msg: str, **kwargs: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def error(self, msg: str, **kwargs: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def warning(self, msg: str, **kwargs: Any) -> None:
        raise NotImplementedError
