from src.application.gateways.billing_gateway import BillingGateway
from src.domain.billing.value_objects.account_balance import AccountBalance


class GetUsageSummaryUseCase:
    def __init__(self, billing_gateway: BillingGateway) -> None:
        self._billing_gateway = billing_gateway

    async def execute(self) -> AccountBalance:
        return await self._billing_gateway.get_balance()
