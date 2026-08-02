#!/usr/bin/env bash
#
# deploy.sh — Despliegue Continuo (CD) por SSH directo.
#
# Uso:
#   ./scripts/deploy.sh [vps-host]
#
# El host puede indicarse como IP o usuario@IP:
#   ./scripts/deploy.sh 168.181.184.103
#   ./scripts/deploy.sh root@168.181.184.103
#
# El puerto viaja en VPS_PORT (por defecto 5932) y puede sobrescribirse por
# entorno:  VPS_PORT=22 ./scripts/deploy.sh
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REMOTE_DIR="/root/proyectos_software/echo-mind"

VPS_RAW="${1:-168.181.184.103}"
VPS_PORT="${VPS_PORT:-5932}"

if [[ "$VPS_RAW" == *@* ]]; then
    VPS_TARGET="$VPS_RAW"
else
    VPS_TARGET="root@$VPS_RAW"
fi

# Colores para salidas legibles en terminal.
if [ -t 1 ]; then
    BOLD="\033[1m"
    GREEN="\033[32m"
    YELLOW="\033[33m"
    RESET="\033[0m"
else
    BOLD=""
    GREEN=""
    YELLOW=""
    RESET=""
fi

echo "==> Desplegando en ${VPS_TARGET}:${VPS_PORT} (${REMOTE_DIR})..."

ssh -T \
    -o ConnectTimeout=10 \
    -p "${VPS_PORT}" \
    "${VPS_TARGET}" \
    bash -s <<EOF
set -euo pipefail

cd "${REMOTE_DIR}"

echo ""
echo "==> [1/4] ${BOLD}Git Pull${RESET} (git pull origin main)..."
git pull origin main

echo ""
echo "==> [2/4] ${BOLD}Restart${RESET} (systemctl restart echo-mind)..."
systemctl restart echo-mind

echo ""
echo "==> [3/4] ${BOLD}Status${RESET} (systemctl status echo-mind)..."
systemctl status echo-mind --no-pager

echo ""
echo "==> [4/4] ${BOLD}Logs${RESET} (journalctl -u echo-mind -n 15)..."
journalctl -u echo-mind -n 15 --no-pager

echo ""
echo "${GREEN}${BOLD}==> ✔ Despliegue completado con éxito.${RESET}"
EOF
