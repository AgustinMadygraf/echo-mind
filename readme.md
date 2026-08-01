# Echo Mind 🧠🎙️

> **Telegram Voice Summarizer Bot** — Servidor asíncrono desarrollado bajo Clean Architecture, Screaming Architecture y principios DDD/SOLID para la transcripción, análisis estructurado y generación de resúmenes ejecutivos a partir de notas de voz.

---

## 📐 Arquitectura del Sistema

```text
               ┌──────────────────────────────────────────┐
               │    DELIVERY MECHANISM / INFRASTRUCTURE   │
               │        (python-telegram-bot, httpx)      │
               └────────────────────┬─────────────────────┘
                                    │ Inyección de Dependencias
                                    ▼
               ┌──────────────────────────────────────────┐
               │         APPLICATION & USE CASES          │
               │  (ProcessVoiceNoteUseCase, Presenters)   │
               └────────────────────┬─────────────────────┘
                                    │ Puertos / Gateways (DIP)
                                    ▼
               ┌──────────────────────────────────────────┐
               │              DOMAIN LAYER                │
               │     (VoiceNote, AudioSummary, VO)        │
               └──────────────────────────────────────────┘

```

* **Dominio Puro:** Entidades e inmutables (`dataclasses frozen=True`) independientes de cualquier framework o librería externa.
* **Caso de Uso Central:** Inyección explícita de contratos (`STTGateway` y `LLMGateway`) mediante Inversión de Dependencias (DIP).
* **Observabilidad Transversal:** Medición de latencias (`perf_counter`) y logging de eventos mediante el **Patrón Decorador** (`ObservedProcessVoiceNoteUseCase`), manteniendo el caso de uso base 100% libre de código de telemetría.
* **Formato Seguro:** Generación de respuestas con escapado HTML y límites de tamaño ajustados para la API de Telegram.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Rol |
| --- | --- | --- |
| **Lenguaje** | Python 3.11+ | Runtime principal |
| **Interface** | `python-telegram-bot` | Polling y descarga asíncrona de archivos |
| **STT Engine** | Groq API (`whisper-large-v3`) | Transcripción de audio ultra-rápida |
| **LLM Engine** | DeepSeek API (`deepseek-chat`) | Análisis estructurado en formato JSON |
| **HTTP Client** | `httpx` (Async) | Peticiones I/O no bloqueantes |
| **Configuración** | `pydantic-settings` / `python-dotenv` | Gestión segura de variables de entorno |

---

## 📁 Estructura del Proyecto

```text
echo-mind/
├── src/
│   ├── domain/                         # Capa de Dominio (Modelos Puros)
│   │   ├── entities/
│   │   │   └── voice_note.py
│   │   └── value_objects/
│   │       └── audio_analysis.py
│   ├── application/                    # Casos de Uso y Contratos (Ports)
│   │   ├── gateways/
│   │   │   ├── stt_gateway.py
│   │   │   ├── llm_gateway.py
│   │   │   └── logger_gateway.py
│   │   ├── presenters/
│   │   │   └── telegram_presenter.py
│   │   └── use_cases/
│   │       ├── process_voice_note.py
│   │       └── observed_process_voice_note.py
│   ├── infrastructure/                 # Adaptadores Concretos (HTTP, Telegram, Logging)
│   │   ├── groq/
│   │   │   └── groq_stt_adapter.py
│   │   ├── deepseek/
│   │   │   └── deepseek_llm_adapter.py
│   │   ├── logging/
│   │   │   └── structured_logger.py
│   │   └── telegram/
│   │       └── telegram_controller.py
│   ├── config/
│   │   └── settings.py
│   └── main.py                         # Composition Root (Punto de Entrada)
├── run.sh                              # Script ejecutable de entorno
├── echo-mind.service                   # Definición para systemd (VPS)
├── DEPLOYMENT.md                       # Guía de despliegue
└── .env.example                        # Plantilla de variables de entorno

```

---

## 🚀 Guía de Instalación y Uso Local

### 1. Requisitos Previos

* Python 3.10+
* Entorno Linux/macOS
* API Keys activas para Telegram, Groq y DeepSeek.

### 2. Configuración del Entorno

Clona el repositorio e instala las dependencias dentro del entorno virtual:

```bash
git clone [https://github.com/tu-usuario/echo-mind.git](https://github.com/tu-usuario/echo-mind.git)
cd echo-mind

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

Crea el archivo `.env` a partir de la plantilla:

```bash
cp .env.example .env

```

Edita `.env` con tus credenciales:

```env
TELEGRAM_BOT_TOKEN="tu_token_de_telegram"
GROQ_API_KEY="tu_api_key_de_groq"
DEEPSEEK_API_KEY="tu_api_key_de_deepseek"

```

### 3. Ejecución

Concede permisos y ejecuta el script de arranque:

```bash
chmod +x run.sh
./run.sh

```

---

## 🔒 Seguridad y Observabilidad

1. **RedactingFilter:** El sistema de logging incluye un filtro de sanitización que reemplaza automáticamente cualquier ocurrencia de los tokens y API keys por `***REDACTED***` en los registros.
2. **Manejo de Errores Seguro:** Las excepciones de red e infraestructura son capturadas en adaptadores concretos. El cliente final de Telegram recibe exclusivamente mensajes genéricos y amigables, evitando fugas de información interna (*Information Disclosure*).
3. **Escapado HTML Integrado:** Todo el texto dinámico procesado por el LLM pasa por `html.escape()` antes de ser inyectado en las plantillas de mensaje.

---

## 📜 Licencia

Desarrollado bajo licencia MIT. Libre para uso, modificación y distribución.
