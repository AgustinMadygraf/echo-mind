import html

from src.domain.value_objects.audio_analysis import AudioSummary

MAX_LENGTH = 4000


class TelegramVoiceSummaryPresenter:
    @staticmethod
    def format_response(summary: AudioSummary) -> str:
        summary_text = html.escape(summary.summary)
        question_text = html.escape(summary.clarification_question)

        message = (
            "<b>📝 Resumen:</b>\n"
            f"{summary_text}\n\n"
            "<b>🤔 Pregunta de clarificación:</b>\n"
            f"{question_text}"
        )

        if len(message) > MAX_LENGTH:
            message = message[:MAX_LENGTH]
            message += "\n\n<i>...[Resumen truncado por límite de longitud]</i>"

        return message
