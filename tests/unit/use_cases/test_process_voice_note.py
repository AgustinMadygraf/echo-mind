import asyncio
import unittest
from unittest.mock import AsyncMock

from src.application.use_cases.process_voice_note import (
    EmptyTranscriptionError,
    ProcessVoiceNoteUseCase,
)
from src.domain.entities.voice_note import VoiceNote
from src.domain.value_objects.audio_analysis import AudioSummary, Transcription


class ProcessVoiceNoteUseCaseTest(unittest.TestCase):
    def _build_voice_note(self) -> VoiceNote:
        return VoiceNote(file_id="f1", file_bytes=b"audio", file_name="f1.ogg", duration=5)

    def test_returns_audio_summary_with_mocked_gateways(self) -> None:
        stt = AsyncMock()
        stt.transcribe.return_value = Transcription(text="Hola mundo", duration_seconds=5.0)
        llm = AsyncMock()
        llm.analyze_transcription.return_value = AudioSummary(
            summary="Resumen", clarification_question="¿Pregunta?"
        )

        use_case = ProcessVoiceNoteUseCase(stt_gateway=stt, llm_gateway=llm)
        result = asyncio.run(use_case.execute(self._build_voice_note()))

        self.assertIsInstance(result, AudioSummary)
        self.assertEqual(result.summary, "Resumen")
        self.assertEqual(result.clarification_question, "¿Pregunta?")
        stt.transcribe.assert_awaited_once()
        llm.analyze_transcription.assert_awaited_once()

    def test_raises_empty_transcription_error(self) -> None:
        stt = AsyncMock()
        stt.transcribe.return_value = Transcription(text="   ", duration_seconds=5.0)
        llm = AsyncMock()

        use_case = ProcessVoiceNoteUseCase(stt_gateway=stt, llm_gateway=llm)
        with self.assertRaises(EmptyTranscriptionError):
            asyncio.run(use_case.execute(self._build_voice_note()))

        stt.transcribe.assert_awaited_once()
        llm.analyze_transcription.assert_not_awaited()

    def test_does_not_call_llm_when_transcription_empty(self) -> None:
        stt = AsyncMock()
        stt.transcribe.return_value = Transcription(text="", duration_seconds=0.0)
        llm = AsyncMock()

        use_case = ProcessVoiceNoteUseCase(stt_gateway=stt, llm_gateway=llm)
        with self.assertRaises(EmptyTranscriptionError):
            asyncio.run(use_case.execute(self._build_voice_note()))
        llm.analyze_transcription.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
