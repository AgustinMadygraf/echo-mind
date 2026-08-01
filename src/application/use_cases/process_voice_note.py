from src.application.gateways.llm_gateway import LLMGateway
from src.application.gateways.stt_gateway import STTGateway
from src.application.use_cases.observed_process_voice_note import VoiceNoteUseCase
from src.domain.entities.voice_note import VoiceNote
from src.domain.value_objects.audio_analysis import AudioSummary


class EmptyTranscriptionError(ValueError):
    """Se lanza cuando la transcripción del STT devuelve texto vacío."""


class ProcessVoiceNoteUseCase(VoiceNoteUseCase):
    def __init__(self, stt_gateway: STTGateway, llm_gateway: LLMGateway) -> None:
        self._stt_gateway = stt_gateway
        self._llm_gateway = llm_gateway

    async def execute(self, voice_note: VoiceNote) -> AudioSummary:
        transcription = await self._stt_gateway.transcribe(voice_note)

        text = (transcription.text or "").strip()
        if not text:
            raise EmptyTranscriptionError("La transcripción devolvió texto vacío")

        return await self._llm_gateway.analyze_transcription(transcription)
