from typing import Any

from src.application.gateways.logger_gateway import LoggerGateway
from src.application.use_cases.voice_note_use_case import UseCaseTiming, VoiceNoteUseCase
from src.domain.entities.voice_note import VoiceNote
from src.domain.value_objects.audio_analysis import AudioSummary


class ObservedProcessVoiceNoteUseCase(VoiceNoteUseCase):
    """Decorator that adds latency measurement and event logging around a
    `VoiceNoteUseCase`."""

    def __init__(self, use_case: VoiceNoteUseCase, logger: LoggerGateway) -> None:
        self._decorated = use_case
        self._logger = logger

    def _emit(self, message: str, **metrics: Any) -> None:
        self._logger.info(message, **metrics)

    async def execute(
        self,
        voice_note: VoiceNote,
        timing: UseCaseTiming | None = None,
    ) -> AudioSummary:
        from time import perf_counter

        inner_timing = timing if timing is not None else UseCaseTiming()
        total_start = perf_counter()
        summary = await self._decorated.execute(voice_note, inner_timing)
        total_duration_ms = (perf_counter() - total_start) * 1000

        self._emit(
            "Voice note processed successfully",
            file_id=voice_note.file_id,
            stt_duration_ms=round(inner_timing.stt_duration_ms or 0, 2),
            llm_duration_ms=round(inner_timing.llm_duration_ms or 0, 2),
            total_duration_ms=round(total_duration_ms, 2),
        )
        return summary
