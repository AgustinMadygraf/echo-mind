import html

from src.domain.billing.value_objects.account_balance import AccountBalance


class UsagePresenter:
    @staticmethod
    def format_balance(balance: AccountBalance) -> str:
        amount = f"{balance.balance_usd:,.2f}"
        return (
            "<b>📊 Estado de Cuenta DeepSeek:</b> "
            f"{html.escape(amount)} {html.escape(balance.currency)}"
        )

    @staticmethod
    def format_error() -> str:
        return (
            "⚠️ <b>Error:</b> No fue posible consultar el estado de cuenta. "
            "Por favor intenta nuevamente."
        )
