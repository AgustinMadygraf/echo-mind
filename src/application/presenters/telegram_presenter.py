from src.domain.value_objects.audio_analysis import AudioSummary


class TelegramVoiceSummaryPresenter:
    @staticmethod
    def format_response(summary: AudioSummary) -> str:
        return (
            "📝 *Resumen*\n"
            f"{summary.summary}\n\n"
            "🤔 *Pregunta de clarificación*\n"
            f"{summary.clarification_question}"
        )
