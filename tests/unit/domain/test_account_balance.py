import unittest

from src.domain.billing.value_objects.account_balance import AccountBalance


class AccountBalanceTest(unittest.TestCase):
    def test_instantiates_correctly(self) -> None:
        balance = AccountBalance(
            provider="DeepSeek",
            balance_usd=12.5,
            currency="USD",
            is_available=True,
        )
        self.assertEqual(balance.provider, "DeepSeek")
        self.assertEqual(balance.balance_usd, 12.5)
        self.assertEqual(balance.currency, "USD")
        self.assertTrue(balance.is_available)

    def test_instantiates_unavailable(self) -> None:
        balance = AccountBalance(
            provider="DeepSeek",
            balance_usd=0.0,
            currency="USD",
            is_available=False,
        )
        self.assertFalse(balance.is_available)


if __name__ == "__main__":
    unittest.main()
