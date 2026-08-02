import html

from src.domain.value_objects.audio_analysis import AudioSummary
from src.infrastructure.telegram.formatters import clean_telegram_html

MAX_LENGTH = 4000


class TelegramVoiceSummaryPresenter:
    @staticmethod
    def _truncate(message: str) -> str:
        if len(message) <= MAX_LENGTH:
            return message
        message = message[:MAX_LENGTH]
        message += "\n\n<i>...[Resumen truncado por límite de longitud]</i>"
        return message

    @staticmethod
    def format_summary(summary: AudioSummary) -> str:
        summary_text = html.escape(clean_telegram_html(summary.summary))
        message = f"<b>📝 Resumen:</b>\n{summary_text}"
        return TelegramVoiceSummaryPresenter._truncate(message)

    @staticmethod
    def format_question(summary: AudioSummary) -> str:
        question_text = html.escape(clean_telegram_html(summary.clarification_question))
        message = f"<b>🤔 Pregunta de clarificación:</b>\n{question_text}"
        return TelegramVoiceSummaryPresenter._truncate(message)
