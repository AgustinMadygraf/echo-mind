from typing import cast

import httpx

from src.application.gateways.billing_gateway import BillingGateway
from src.application.gateways.logger_gateway import LoggerGateway
from src.domain.billing.value_objects.account_balance import AccountBalance


class DeepSeekBillingError(Exception):
    """Error de infraestructura al comunicarse con el saldo de DeepSeek."""


class DeepSeekBillingAdapter(BillingGateway):
    def __init__(
        self,
        api_key: str,
        logger: LoggerGateway,
        api_url: str = "https://api.deepseek.com/user/balance",
    ) -> None:
        self._api_key = api_key
        self._logger = logger
        self._api_url = api_url

    async def get_balance(self) -> AccountBalance:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self._api_url, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            response = exc.response
            self._logger.error(
                "DeepSeek balance request failed",
                status_code=response.status_code,
                response_body=response.text,
            )
            raise DeepSeekBillingError(
                f"Fallo al consultar el saldo en DeepSeek (HTTP {response.status_code})"
            ) from exc
        except httpx.HTTPError as exc:
            self._logger.error(
                "DeepSeek balance request failed",
                detail=str(exc),
            )
            raise DeepSeekBillingError(
                f"Fallo al consultar el saldo en DeepSeek: {exc}"
            ) from exc

        return self._parse_balance(payload)

    def _parse_balance(self, payload: dict[str, object]) -> AccountBalance:
        try:
            # La API devuelve la estructura directamente en la raíz:
            #   {"is_available": true, "balance_infos": [{"currency", "total_balance", ...}]}
            data: dict[str, object] = cast(
                dict[str, object],
                payload.get("data", payload),
            )
            is_available = bool(data.get("is_available", False))
            balance_infos = cast(
                list[dict[str, object]],
                data.get("balance_infos", []),
            )
            currency: str = "USD"
            balance_usd = 0.0
            for info in balance_infos:
                total_balance = info.get("total_balance")
                if total_balance is not None:
                    balance_usd = float(str(total_balance))
                    fetched_currency = info.get("currency")
                    if isinstance(fetched_currency, str):
                        currency = fetched_currency
                    break
        except (TypeError, ValueError) as exc:
            self._logger.error(
                "DeepSeek balance response could not be parsed",
                detail=str(exc),
                response_body=str(payload),
            )
            raise DeepSeekBillingError(
                f"Fallo al interpretar el saldo de DeepSeek: {exc}"
            ) from exc

        return AccountBalance(
            provider="DeepSeek",
            balance_usd=balance_usd,
            currency=currency,
            is_available=is_available,
        )
