from datetime import timedelta

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.application.use_cases.observed_process_voice_note import VoiceNoteUseCase
from src.application.use_cases.process_voice_note import EmptyTranscriptionError
from src.domain.entities.voice_note import VoiceNote
from src.infrastructure.telegram.telegram_presenter import TelegramVoiceSummaryPresenter


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
                chat_id=update.message.chat_id, action="record_voice"
            )

            file = await context.bot.get_file(file_id=audio.file_id)
            file_bytes = await file.download_as_bytearray()

            audio_duration = audio.duration
            if isinstance(audio_duration, timedelta):
                audio_duration = int(audio_duration.total_seconds())

            voice_note = VoiceNote(
                file_id=audio.file_id,
                file_bytes=bytes(file_bytes),
                file_name=f"{audio.file_id}.ogg",
                duration=audio_duration,
            )

            summary = await self._use_case.execute(voice_note)
            await processing_message.edit_text(
                TelegramVoiceSummaryPresenter.format_summary(summary),
                parse_mode=ParseMode.HTML,
            )
            await update.message.reply_text(
                TelegramVoiceSummaryPresenter.format_question(summary),
                parse_mode=ParseMode.HTML,
            )
        except EmptyTranscriptionError:
            await processing_message.edit_text(
                "⚠️ <b>Audio no procesable:</b> No se detectó ninguna "
                "transcripción de voz clara en la nota enviada.",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await processing_message.edit_text(
                "❌ <b>Error:</b> No fue posible procesar tu nota de voz en "
                "este momento. Por favor intenta nuevamente.",
                parse_mode=ParseMode.HTML,
            )
