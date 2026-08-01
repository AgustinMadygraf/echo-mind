from abc import ABC, abstractmethod

from src.domain.entities.voice_note import VoiceNote
from src.domain.value_objects.audio_analysis import AudioSummary


class UseCaseTiming:
    """Collects per-step latencies measured inside the use case."""

    def __init__(self) -> None:
        self.stt_duration_ms: float | None = None
        self.llm_duration_ms: float | None = None


class VoiceNoteUseCase(ABC):
    """Port for the process-voice-note use case."""

    @abstractmethod
    async def execute(
        self,
        voice_note: VoiceNote,
        timing: UseCaseTiming | None = None,
    ) -> AudioSummary:
        raise NotImplementedError
