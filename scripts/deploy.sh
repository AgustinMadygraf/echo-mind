#!/usr/bin/env bash
#
# deploy.sh — Despliegue Continuo (CD) por SSH directo.
#
# Uso:
#   ./scripts/deploy.sh [vps-host]
#
# El host por defecto es "root@vps-ip". También puede configurarse
# exportando VPS_HOST.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REMOTE_DIR="/root/proyectos_software/echo-mind"

VPS_HOST="${VPS_HOST:-root@vps-ip}"
if [ "${1:-}" != "" ]; then
    VPS_HOST="$1"
fi

echo "==> Desplegando en ${VPS_HOST} (${REMOTE_DIR})..."

ssh "${VPS_HOST}" <<EOF
set -e

cd "${REMOTE_DIR}"

echo "==> [1/5] Actualizando código (git pull origin main)..."
git pull origin main

echo "==> [2/5] Reiniciando servicio echo-mind..."
systemctl restart echo-mind

echo "==> [3/5] Estado del servicio..."
systemctl status echo-mind --no-pager

echo "==> [4/5] Últimas líneas de logs (15)..."
journalctl -u echo-mind -n 15 --no-pager

echo "==> [5/5] Despliegue completado."
EOF
