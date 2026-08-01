import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from src.application.use_cases.billing.get_usage_summary import GetUsageSummaryUseCase
from src.application.use_cases.observed_process_voice_note import (
    ObservedProcessVoiceNoteUseCase,
)
from src.application.use_cases.process_voice_note import ProcessVoiceNoteUseCase
from src.config.settings import Settings
from src.infrastructure.billing import DeepSeekBillingAdapter
from src.infrastructure.httpx import DeepSeekLLMAdapter
from src.infrastructure.httpx import GroqSTTAdapter
from src.infrastructure.logging.structured_logger import StructuredLoggerAdapter
from src.infrastructure.telegram.telegram_controller import TelegramController
from src.infrastructure.telegram.usage_command_handler import UsageCommandHandler


def build_app() -> None:
    settings = Settings.from_env()

    logger = StructuredLoggerAdapter(
        secrets=[
            settings.groq_api_key,
            settings.deepseek_api_key,
            settings.telegram_bot_token,
        ]
    )

    stt_gateway = GroqSTTAdapter(
        api_key=settings.groq_api_key, logger=logger
    )
    llm_gateway = DeepSeekLLMAdapter(
        api_key=settings.deepseek_api_key, logger=logger
    )
    use_case = ProcessVoiceNoteUseCase(
        stt_gateway=stt_gateway, llm_gateway=llm_gateway
    )
    observed_use_case = ObservedProcessVoiceNoteUseCase(
        use_case=use_case, logger=logger
    )
    telegram_controller = TelegramController(use_case=observed_use_case)

    billing_gateway = DeepSeekBillingAdapter(
        api_key=settings.deepseek_api_key, logger=logger
    )
    usage_use_case = GetUsageSummaryUseCase(billing_gateway=billing_gateway)
    usage_handler = UsageCommandHandler(use_case=usage_use_case)

    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )
    app.add_handler(
        CommandHandler("usage", usage_handler.handle_usage)
    )
    app.add_handler(
        MessageHandler(filters.VOICE | filters.AUDIO, telegram_controller.handle_voice_note)
    )
    app.run_polling()


if __name__ == "__main__":
    build_app()
