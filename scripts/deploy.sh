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

echo "==> Desplegando en ${VPS_TARGET}:${VPS_PORT} (${REMOTE_DIR})..."

ssh -T \
    -o ConnectTimeout=10 \
    -p "${VPS_PORT}" \
    "${VPS_TARGET}" \
    bash -s <<EOF
set -euo pipefail

cd "${REMOTE_DIR}"

echo ""
echo -e "==> [1/4] \033[1mGit Pull\033[0m (git pull origin main)..."
git pull origin main

echo ""
echo -e "==> [2/4] \033[1mRestart\033[0m (systemctl restart echo-mind)..."
systemctl restart echo-mind

echo ""
echo -e "==> [3/4] \033[1mStatus\033[0m (systemctl status echo-mind)..."
systemctl status echo-mind --no-pager

echo ""
echo -e "==> [4/4] \033[1mLogs\033[0m (journalctl -u echo-mind -n 15)..."
journalctl -u echo-mind -n 15 --no-pager

echo ""
echo -e "\033[32m\033[1m==> ✔ Despliegue completado con éxito.\033[0m"
EOF
