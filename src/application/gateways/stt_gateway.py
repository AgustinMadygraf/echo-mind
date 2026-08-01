from abc import ABC, abstractmethod

from src.domain.entities.voice_note import VoiceNote
from src.domain.value_objects.audio_analysis import Transcription


class STTGateway(ABC):
    @abstractmethod
    async def transcribe(self, voice_note: VoiceNote) -> Transcription:
        raise NotImplementedError
