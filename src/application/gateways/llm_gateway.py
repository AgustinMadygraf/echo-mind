from abc import ABC, abstractmethod

from src.domain.value_objects.audio_analysis import AudioSummary, Transcription


class LLMGateway(ABC):
    @abstractmethod
    async def analyze_transcription(self, transcription: Transcription) -> AudioSummary:
        raise NotImplementedError
