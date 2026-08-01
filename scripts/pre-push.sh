#!/usr/bin/env bash
#
# pre-push.sh — Pipeline local de CI antes de cada push.
# Ejecuta compilación y suite de pruebas; aborta con exit != 0 si algo falla.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> [1/2] Compilando todos los módulos (python3 -m compileall src)..."
if python3 -m compileall -q src; then
    echo "    ✔ Compilación OK"
else
    echo "    ✘ Compilación fallida"
    exit 1
fi

echo "==> [2/2] Ejecutando suite de pruebas unitarias..."
if python3 -m unittest discover -s tests; then
    echo "    ✔ Tests OK"
else
    echo "    ✘ Test(s) fallido(s)"
    exit 1
fi

echo "==> ✔ Pipeline local completado con éxito."
