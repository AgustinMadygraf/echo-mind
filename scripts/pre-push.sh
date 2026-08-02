#!/usr/bin/env bash
#
# pre-push.sh — Pipeline local de CI antes de cada push.
# Ejecuta: ruff (auto-fix), pyright, compilación y suite de pruebas.
# Aborta con exit != 0 si cualquiera de las verificaciones falla.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Usar el venv del proyecto si existe; si no, python3 del sistema.
if [ -x "venv/bin/python" ]; then
    PY="venv/bin/python"
else
    PY="python3"
fi

echo "==> [1/4] Ruff (lint + auto-fix) sobre src y tests..."
if "$PY" -m ruff check src tests --fix; then
    echo "    ✔ Ruff OK"
else
    echo "    ✘ Ruff encontró errores no auto-corregibles"
    exit 1
fi

echo "==> [2/4] Pyright (verificación de tipos) sobre src..."
if "$PY" -m pyright src; then
    echo "    ✔ Pyright OK"
else
    echo "    ✘ Pyright encontró errores de tipos"
    exit 1
fi

echo "==> [3/4] Compilando todos los módulos (compileall src)..."
if "$PY" -m compileall -q src; then
    echo "    ✔ Compilación OK"
else
    echo "    ✘ Compilación fallida"
    exit 1
fi

echo "==> [4/4] Ejecutando suite de pruebas unitarias (unittest)..."
if "$PY" -m unittest discover -s tests; then
    echo "    ✔ Tests OK"
else
    echo "    ✘ Test(s) fallido(s)"
    exit 1
fi

echo "==> ✔ Pipeline local completado con éxito."
