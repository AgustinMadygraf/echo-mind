#!/usr/bin/env bash
set -e

# Posicionarse en el directorio del script
cd "$(dirname "$0")"

# Verificar existencia del venv
if [ ! -d "venv" ]; then
    echo "❌ Error: El entorno virtual 'venv' no existe. Ejecuta primero la instalación de dependencias."
    exit 1
fi

# Cargar variables de entorno si existe .env
if [ -f ".env" ]; then
    echo "ℹ️  Cargando variables de entorno desde .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Activar venv y ejecutar main.py
source venv/bin/activate
echo "🚀 Iniciando echo-mind bot..."
exec python src/main.py
