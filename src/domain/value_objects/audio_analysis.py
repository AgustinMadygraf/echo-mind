from dataclasses import dataclass


@dataclass(frozen=True)
class Transcription:
    text: str
    duration_seconds: float | None = None


@dataclass(frozen=True)
class AudioSummary:
    summary: str
    clarification_question: str
