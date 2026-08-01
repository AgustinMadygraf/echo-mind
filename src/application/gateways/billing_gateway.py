from abc import ABC, abstractmethod

from src.domain.billing.value_objects.account_balance import AccountBalance


class BillingGateway(ABC):
    @abstractmethod
    async def get_balance(self) -> AccountBalance:
        raise NotImplementedError
