from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.application.use_cases.billing.get_usage_summary import GetUsageSummaryUseCase
from src.infrastructure.telegram.usage_presenter import UsagePresenter


class UsageCommandHandler:
    def __init__(self, use_case: GetUsageSummaryUseCase) -> None:
        self._use_case = use_case

    async def handle_usage(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        assert update.message is not None
        try:
            balance = await self._use_case.execute()
            message = UsagePresenter.format_balance(balance)
        except Exception:
            message = UsagePresenter.format_error()
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
