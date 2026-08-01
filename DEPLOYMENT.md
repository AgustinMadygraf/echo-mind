# Echo Mind — Guía de Despliegue y CD

Guía para desplegar el bot de Telegram **Echo Mind** en una VPS mediante
systemd, con un flujo de **Despliegue Continuo** vía SSH directo.

## Requisitos previos

- VPS con Ubuntu/Debian (o similar), acceso root por SSH.
- Python 3.10+ y `git` instalados en la VPS.
- Credenciales: `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`, `DEEPSEEK_API_KEY`.
- Acceso por SSH desde la máquina local a la VPS (claves o password).

## Configuración inicial de la VPS (una sola vez)

### 1. Clonar el repositorio

```bash
mkdir -p /root/proyectos_software
cd /root/proyectos_software
git clone <URL_DEL_REPOSITORIO> echo-mind
cd echo-mind
```

### 2. Crear el entorno virtual e instalar dependencias

```bash
cd /root/proyectos_software/echo-mind
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Crear el archivo `.env`

```bash
cd /root/proyectos_software/echo-mind
cp .env.example .env
nano .env
```

Llena con las credenciales reales:

```
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
GROQ_API_KEY=tu_groq_api_key
DEEPSEEK_API_KEY=tu_deepseek_api_key
```

> **Importante:** `.env` NO se sube al repositorio. Está en `.gitignore` y se
> mantiene solo en la VPS.

### 4. Dar permisos de ejecución a los scripts

```bash
cd /root/proyectos_software/echo-mind
chmod +x run.sh scripts/*.sh
```

### 5. Instalar el servicio systemd

```bash
cp echo-mind.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now echo-mind
```

Verifica el estado:

```bash
systemctl status echo-mind --no-pager
```

## Despliegue (CD por SSH directo)

Desde tu máquina local (en la raíz del repo ejecuta el script):

```bash
./scripts/deploy.sh <tu-ip-vps>
```

Internamente el script hace, vía SSH al servidor remoto:

```bash
cd /root/proyectos_software/echo-mind
git pull origin main
systemctl restart echo-mind
systemctl status echo-mind --no-pager
journalctl -u echo-mind -n 15 --no-pager
```

El script aborta con `exit != 0` si algún paso falla. El host por defecto es
`root@vps-ip`; también puede fijarse con la variable de entorno:

```bash
VPS_HOST=root@maquina.example.com ./scripts/deploy.sh
```

## Monitoreo de logs en tiempo real

En la VPS:

```bash
journalctl -u echo-mind -f -o cat
```

Seguimiento sin bloquear (últimas líneas):

```bash
journalctl -u echo-mind -n 50 --no-pager
```

## Notas operativas

- El servicio se reinicia automáticamente ante fallos (`Restart=always`,
  `RestartSec=5`).
- Tras el `git pull`, los cambios de `src/`, `requirements.txt` u otras
  actualizaciones quedan activas con `systemctl restart echo-mind`.
- Si se añaden dependencias nuevas (`requirements.txt`), se debe reinstalar
  el venv manualmente en la VPS antes de reiniciar el servicio.
- `<URL_DEL_REPOSITORIO>` y `<tu-ip-vps>` son marcadores: reemplázalos por tus
  valores reales.
