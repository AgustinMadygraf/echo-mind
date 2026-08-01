from telegram.ext import ApplicationBuilder, MessageHandler, filters

from src.application.controllers.telegram_controller import TelegramController
from src.application.use_cases.process_voice_note import ProcessVoiceNoteUseCase
from src.config.settings import Settings
from src.infrastructure.deepseek import DeepSeekLLMAdapter
from src.infrastructure.groq import GroqSTTAdapter


def build_app() -> None:
    settings = Settings.from_env()

    stt_gateway = GroqSTTAdapter(api_key=settings.groq_api_key)
    llm_gateway = DeepSeekLLMAdapter(api_key=settings.deepseek_api_key)
    use_case = ProcessVoiceNoteUseCase(
        stt_gateway=stt_gateway, llm_gateway=llm_gateway
    )
    telegram_controller = TelegramController(use_case=use_case)

    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )
    app.add_handler(
        MessageHandler(filters.VOICE | filters.AUDIO, telegram_controller.handle_voice_note)
    )
    app.run_polling()


if __name__ == "__main__":
    build_app()
