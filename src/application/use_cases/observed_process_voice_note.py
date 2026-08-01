from abc import ABC, abstractmethod
from typing import Any

from src.application.gateways.logger_gateway import LoggerGateway
from src.domain.entities.voice_note import VoiceNote
from src.domain.value_objects.audio_analysis import AudioSummary


class VoiceNoteUseCase(ABC):
    """Port for the process-voice-note use case, implemented by the concrete
    use case and by the observability decorator."""

    @abstractmethod
    async def execute(self, voice_note: VoiceNote) -> AudioSummary:
        raise NotImplementedError


class ObservedProcessVoiceNoteUseCase(VoiceNoteUseCase):
    """Decorator that adds latency measurement and event logging around a
    `VoiceNoteUseCase`."""

    def __init__(self, use_case: VoiceNoteUseCase, logger: LoggerGateway) -> None:
        self._decorated = use_case
        self._logger = logger

    def _emit(self, message: str, **metrics: Any) -> None:
        self._logger.info(message, **metrics)

    async def execute(self, voice_note: VoiceNote) -> AudioSummary:
        from time import perf_counter

        total_start = perf_counter()
        summary = await self._decorated.execute(voice_note)
        total_duration_ms = (perf_counter() - total_start) * 1000
        self._emit(
            "Voice note processed successfully",
            file_id=voice_note.file_id,
            total_duration_ms=round(total_duration_ms, 2),
        )
        return summary
