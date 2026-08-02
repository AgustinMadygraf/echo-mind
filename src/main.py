import logging
import signal
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters

from src.application.use_cases.billing.get_usage_summary import GetUsageSummaryUseCase
from src.application.use_cases.observed_process_voice_note import (
    ObservedProcessVoiceNoteUseCase,
)
from src.application.use_cases.process_voice_note import ProcessVoiceNoteUseCase
from src.config.settings import Settings
from src.infrastructure.billing import DeepSeekBillingAdapter
from src.infrastructure.httpx import DeepSeekLLMAdapter, GroqSTTAdapter
from src.infrastructure.logging.structured_logger import StructuredLoggerAdapter
from src.infrastructure.telegram.telegram_controller import TelegramController
from src.infrastructure.telegram.usage_command_handler import UsageCommandHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("echo-mind")


_Application = Application[Any, Any, Any, Any, Any, Any]


def build_app() -> _Application:
    settings = Settings.from_env()

    app_logger = StructuredLoggerAdapter(
        secrets=[
            settings.groq_api_key,
            settings.deepseek_api_key,
            settings.telegram_bot_token,
        ]
    )

    http_client = httpx.AsyncClient(timeout=60.0)

    stt_gateway = GroqSTTAdapter(
        api_key=settings.groq_api_key, logger=app_logger, client=http_client
    )
    llm_gateway = DeepSeekLLMAdapter(
        api_key=settings.deepseek_api_key, logger=app_logger, client=http_client
    )
    use_case = ProcessVoiceNoteUseCase(
        stt_gateway=stt_gateway, llm_gateway=llm_gateway
    )
    observed_use_case = ObservedProcessVoiceNoteUseCase(
        use_case=use_case, logger=app_logger
    )
    telegram_controller = TelegramController(use_case=observed_use_case)

    billing_gateway = DeepSeekBillingAdapter(
        api_key=settings.deepseek_api_key, logger=app_logger
    )
    usage_use_case = GetUsageSummaryUseCase(billing_gateway=billing_gateway)
    usage_handler = UsageCommandHandler(use_case=usage_use_case)

    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )
    app.add_handler(CommandHandler("usage", usage_handler.handle_usage))
    app.add_handler(
        MessageHandler(filters.VOICE | filters.AUDIO, telegram_controller.handle_voice_note)
    )

    async def close_http_client(_app: _Application) -> None:
        await http_client.aclose()

    # Graceful shutdown: run_polling cierra la app (shutdown + post_shutdown) al
    # recibir SIGINT/SIGTERM; el hook cierra el cliente HTTP compartido.
    app.post_shutdown = close_http_client
    return app


def main() -> None:
    app = build_app()
    try:
        # run_polling inicializa la app y la detiene de forma elegante
        # (shutdown + post_shutdown) ante SIGINT/SIGTERM (stop_signals).
        app.run_polling(stop_signals=(signal.SIGINT, signal.SIGTERM))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Interrupción recibida, deteniendo aplicación...")
    finally:
        logger.info("Aplicación echo-mind detenida correctamente")


if __name__ == "__main__":
    main()
