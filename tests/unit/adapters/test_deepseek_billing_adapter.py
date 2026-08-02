import asyncio
import io
import logging
import unittest
from unittest.mock import patch

import httpx

from src.domain.billing.value_objects.account_balance import AccountBalance
from src.infrastructure.billing.adapters.deepseek_billing_adapter import (
    DeepSeekBillingAdapter,
)
from src.infrastructure.logging.structured_logger import StructuredLoggerAdapter


class DeepSeekBillingAdapterTest(unittest.TestCase):
    def _adapter(self) -> DeepSeekBillingAdapter:
        buffer = io.StringIO()
        logger = StructuredLoggerAdapter(
            secrets=[],
            handler=logging.StreamHandler(buffer),
            human_readable=False,
        )
        return DeepSeekBillingAdapter(api_key="sk-test", logger=logger)

    def test_gets_balance_from_root_structure(self) -> None:
        payload = {
            "is_available": True,
            "balance_infos": [{"currency": "USD", "total_balance": "1.79"}],
        }

        async def _fake_get(self, url, headers=None, **kwargs):
            request = httpx.Request("GET", url)
            return httpx.Response(200, request=request, json=payload)

        adapter = self._adapter()
        with patch.object(httpx.AsyncClient, "get", new=_fake_get):
            result = asyncio.run(adapter.get_balance())

        self.assertIsInstance(result, AccountBalance)
        self.assertEqual(result.provider, "DeepSeek")
        self.assertEqual(result.balance_usd, 1.79)
        self.assertEqual(result.currency, "USD")
        self.assertTrue(result.is_available)

    def test_gets_balance_from_nested_container_as_fallback(self) -> None:
        # Defensive: la respuesta envuelta en "data" también debe resolverse.
        payload = {
            "data": {
                "is_available": True,
                "balance_infos": [{"currency": "USD", "total_balance": "1.79"}],
            }
        }

        async def _fake_get(self, url, headers=None, **kwargs):
            request = httpx.Request("GET", url)
            return httpx.Response(200, request=request, json=payload)

        adapter = self._adapter()
        with patch.object(httpx.AsyncClient, "get", new=_fake_get):
            result = asyncio.run(adapter.get_balance())

        self.assertEqual(result.balance_usd, 1.79)
        self.assertEqual(result.currency, "USD")
        self.assertTrue(result.is_available)


if __name__ == "__main__":
    unittest.main()
