import json

import httpx

from src.application.gateways.llm_gateway import LLMGateway
from src.domain.value_objects.audio_analysis import AudioSummary, Transcription

SYSTEM_PROMPT = (
    "Eres un asistente que resume notas de voz. Responde exclusivamente en "
    "JSON estructurado con exactamente estas dos llaves: "
    '"summary": un resumen claro, conciso y estructurado del audio en español; '
    'y "clarification_question": una única pregunta específica sobre alguna '
    'duda, ambigüedad o punto clave del audio. Si el audio es 100% claro, '
    "formula una pregunta de seguimiento relevante."
)


class DeepSeekLLMError(Exception):
    """Error de infraestructura al comunicarse con la API de chat de DeepSeek."""


class DeepSeekLLMAdapter(LLMGateway):
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.deepseek.com/v1/chat/completions",
        model: str = "deepseek-chat",
    ) -> None:
        self._api_key = api_key
        self._api_url = api_url
        self._model = model

    async def analyze_transcription(
        self, transcription: Transcription
    ) -> AudioSummary:
        payload = {
            "model": self._model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcription.text},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self._api_url, headers=headers, json=payload
                )
                response.raise_for_status()
                body = response.json()
            content = body["choices"][0]["message"]["content"]
            data = json.loads(content)
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
            raise DeepSeekLLMError(f"Fallo el análisis en DeepSeek: {exc}") from exc

        summary = str(data.get("summary", "")).strip()
        clarification_question = str(data.get("clarification_question", "")).strip()
        return AudioSummary(
            summary=summary, clarification_question=clarification_question
        )
