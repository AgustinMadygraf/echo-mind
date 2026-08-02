import unittest

from src.infrastructure.telegram.formatters import clean_telegram_html


class CleanTelegramHtmlTest(unittest.TestCase):
    def test_converts_escaped_newlines_and_br_to_real_newlines(self) -> None:
        # "Línea 1 \n• <b>Tema</b> <br> Línea 2" con \n literal escapado
        text = "Línea 1 \\n• <b>Tema</b> <br> Línea 2"

        result = clean_telegram_html(text)

        expected = "Línea 1\n• <b>Tema</b>\nLínea 2"
        self.assertEqual(result, expected)
        self.assertNotIn("\\n", result)
        self.assertNotIn("<br", result, msg="deben eliminarse las etiquetas <br>")
        # Verifica que las 3 líneas quedaron separadas por saltos reales.
        self.assertEqual(result.count("\n"), 2)

    def test_empty_input_returns_empty(self) -> None:
        self.assertEqual(clean_telegram_html(""), "")
        self.assertEqual(clean_telegram_html(None), "")

    def test_strips_whitespace_around_real_newlines(self) -> None:
        text = "  Hola   \\n   mundo  "
        self.assertEqual(clean_telegram_html(text), "Hola\nmundo")

    def test_handles_br_variants(self) -> None:
        self.assertEqual(
            clean_telegram_html("a<br>b"),
            "a\nb",
        )
        self.assertEqual(
            clean_telegram_html("a<br/>b"),
            "a\nb",
        )
        self.assertEqual(
            clean_telegram_html("a<br />b"),
            "a\nb",
        )
        self.assertEqual(
            clean_telegram_html("a<BR>b"),
            "a\nb",
        )


if __name__ == "__main__":
    unittest.main()
