"""Helpers de formateo para los presentadores de Telegram.

Estos helpers pertenecen a la capa de entrega (infraestructura), responsable de
garantizar que el HTML enviado a la API de Telegram sea válido y esté limpio.
"""

import re

_BR_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)


def clean_telegram_html(text: str | None) -> str:
    """Normaliza el texto antes de enviarlo con parse_mode=ParseMode.HTML.

    - Reemplaza etiquetas `<br>`, `<br/>` y `<br />` por saltos de línea reales.
    - Convierte cadenas literales escapadas (``\\n`` o ``\\n`` en texto plano)
      a saltos de línea reales.
    - Elimina espacios extra alrededor de cada salto de línea.

    Args:
        text: Texto crudo (potencialmente generado por un LLM) a sanitizar.

    Returns:
        Texto normalizado con saltos de línea reales y sin etiquetas ``<br>``.
    """
    if not text:
        return ""

    # Reemplazar <br> por salto de línea.
    text = _BR_PATTERN.sub("\n", text)
    # Reemplazar saltos de línea literales escapados.
    text = text.replace("\\n", "\n")
    # Eliminar espacios extra antes/después de los saltos de línea.
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines)
