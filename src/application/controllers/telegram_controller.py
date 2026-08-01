from telegram import Update
from telegram.ext import ContextTypes

from src.application.presenters.telegram_presenter import TelegramVoiceSummaryPresenter
from src.application.use_cases.observed_process_voice_note import VoiceNoteUseCase
from src.domain.entities.voice_note import VoiceNote


class TelegramController:
    def __init__(self, use_case: VoiceNoteUseCase) -> None:
        self._use_case = use_case

    async def handle_voice_note(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        assert update.message is not None

        audio = update.message.voice or update.message.audio
        if audio is None:
            await update.message.reply_text(
                "No se pudo leer el mensaje de voz. Envíalo de nuevo."
            )
            return

        processing_message = await update.message.reply_text(
            "⏳ Procesando tu nota de voz..."
        )

        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="record_voice"
            )

            file = await context.bot.get_file(file_id=audio.file_id)
            file_bytes = await file.download_as_bytearray()

            voice_note = VoiceNote(
                file_id=audio.file_id,
                file_bytes=bytes(file_bytes),
                file_name=f"{audio.file_id}.ogg",
                duration=audio.duration,
            )

            summary = await self._use_case.execute(voice_note)
            response = TelegramVoiceSummaryPresenter.format_response(summary)
            await processing_message.edit_text(response)
        except Exception as exc:
            message = (
                "⚠️ Ocurrió un error al procesar tu nota de voz. "
                "Inténtalo nuevamente en unos minutos."
                f"\n\nDetalle: {exc}"
            )
            await processing_message.edit_text(message)
