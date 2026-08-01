from dataclasses import dataclass


@dataclass(frozen=True)
class AccountBalance:
    provider: str
    balance_usd: float
    currency: str
    is_available: bool
