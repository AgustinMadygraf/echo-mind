from src.application.gateways.llm_gateway import LLMGateway
from src.application.gateways.stt_gateway import STTGateway
from src.application.use_cases.voice_note_use_case import UseCaseTiming, VoiceNoteUseCase
from src.domain.entities.voice_note import VoiceNote
from src.domain.value_objects.audio_analysis import AudioSummary


class EmptyTranscriptionError(ValueError):
    """Se lanza cuando la transcripción del STT devuelve texto vacío."""


class ProcessVoiceNoteUseCase(VoiceNoteUseCase):
    def __init__(self, stt_gateway: STTGateway, llm_gateway: LLMGateway) -> None:
        self._stt_gateway = stt_gateway
        self._llm_gateway = llm_gateway

    async def execute(
        self,
        voice_note: VoiceNote,
        timing: UseCaseTiming | None = None,
    ) -> AudioSummary:
        from time import perf_counter

        stt_start = perf_counter()
        transcription = await self._stt_gateway.transcribe(voice_note)
        if timing is not None:
            timing.stt_duration_ms = (perf_counter() - stt_start) * 1000

        text = (transcription.text or "").strip()
        if not text:
            raise EmptyTranscriptionError("La transcripción devolvió texto vacío")

        llm_start = perf_counter()
        summary = await self._llm_gateway.analyze_transcription(transcription)
        if timing is not None:
            timing.llm_duration_ms = (perf_counter() - llm_start) * 1000

        return summary
