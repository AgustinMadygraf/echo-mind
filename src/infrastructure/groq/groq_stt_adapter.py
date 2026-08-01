import httpx

from src.application.gateways.logger_gateway import LoggerGateway
from src.application.gateways.stt_gateway import STTGateway
from src.domain.entities.voice_note import VoiceNote
from src.domain.value_objects.audio_analysis import Transcription


class GroqSTTError(Exception):
    """Error de infraestructura al comunicarse con la API de transcripción de Groq."""


class GroqSTTAdapter(STTGateway):
    def __init__(
        self,
        api_key: str,
        logger: LoggerGateway,
        api_url: str = "https://api.groq.com/openai/v1/audio/transcriptions",
        model: str = "whisper-large-v3",
    ) -> None:
        self._api_key = api_key
        self._logger = logger
        self._api_url = api_url
        self._model = model

    async def transcribe(self, voice_note: VoiceNote) -> Transcription:
        file_name = voice_note.file_name or voice_note.file_id or "audio.ogg"
        files = {"file": (file_name, voice_note.file_bytes, "audio/ogg")}
        data = {"model": self._model}

        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self._api_url, headers=headers, data=data, files=files
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            response = exc.response
            self._logger.error(
                "Groq STT request failed",
                status_code=response.status_code,
                response_body=response.text,
                file_id=voice_note.file_id,
            )
            raise GroqSTTError(
                f"Fallo la transcripción en Groq (HTTP {response.status_code})"
            ) from exc
        except httpx.HTTPError as exc:
            self._logger.error(
                "Groq STT request failed",
                detail=str(exc),
                file_id=voice_note.file_id,
            )
            raise GroqSTTError(f"Fallo la transcripción en Groq: {exc}") from exc

        text = payload.get("text", "").strip()
        duration: float | None = (
            float(voice_note.duration) if voice_note.duration is not None else None
        )
        return Transcription(text=text, duration_seconds=duration)
