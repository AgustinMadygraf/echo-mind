# AGENTS.md — Convenciones del proyecto Echo Mind

Reglas persistentes que todo agente de IA o desarrollador debe respetar al
modificar el código de este repositorio.

## Arquitectura

- **Clean Architecture (regla de dependencia).** Las dependencias apuntan
  estrictamente hacia adentro:
  `infraestructura → aplicación → dominio`. `src/domain/` **nunca** importa
  infraestructura, framework (`telegram`, `httpx`) ni librerías externas de
  I/O. La capa de Aplicación tampoco debe depender del framework.
- **Delivery Mechanism separado.** Los controladores y presentadores de
  Telegram (`src/infrastructure/telegram/`) son infraestructura de entrada.
  No colocar imports de `telegram` ni `html` en `src/application/` ni
  `src/domain/`.
- **DIP.** Las dependencias se inyectan por constructor (interfaces abstractas,
  ej. `STTGateway`, `LLMGateway`, `BillingGateway`, `LoggerGateway`). Nada de
  singletons ni referencias globales; la composición ocurre solo en
  `src/main.py` (Composition Root).

## Tipado estricto (Python 3.12)

- Usa **dataclasses inmutables** (`@dataclass(frozen=True)`) para entidades y
  Value Objects del dominio.
- Usa la **sintaxis genérica moderna de Python 3.12**: `dict[str, object]`,
  `list[str]`, `tuple[int, ...]`. Nunca `dict`, `list` o `tuple` sin parámetros
  de tipo, salvo que la librería no lo permita.
- **No uses `Any` para "resolver" errores de tipos.** Prefiere tipar con
  precisión (`cast(...)`, narrowing con `isinstance`) o acotar el modelo.
- Parámetros de tipos genéricos de terceros (ej. `Application[...]`) deben
  declararse con un alias tipado, no quedarse como genéricos sin argumentos.

## Integraciones resilientes

- **Nunca asumas claves envolventes** como `"data"` en respuestas JSON de APIs
  externas sin antes verificar la raíz con `.get()`.
  Ejemplo correcto: `payload.get("data", payload)`.
- Convierte explícitamente tipos de campo antes de usar: p. ej.
  `float(str(total_balance))` para montos que llegan como string.
- Traduce siempre las excepciones HTTP/red (`httpx.HTTPError`, etc.) a
  excepciones propias de integración (`GroqSTTError`, `DeepSeekLLMError`,
  `DeepSeekBillingError`). No dejes que errores de librerías crucen a capas
  superiores (sin leake de abstracciones).

## Logging y seguridad

- Registra mediante `LoggerGateway` (`src/application/gateways/logger_gateway.py`),
  nunca con `print`.
- El adapter `StructuredLoggerAdapter` aplica `RedactingFilter` que reemplaza
  secretos (API keys/tokens) por `***REDACTED***` en el mensaje y los campos
  estructurados. No registres credenciales ni los re-expongas en `str(exc)`.
- Los logs son JSON estructurado en entornos no interactivos; formato legible
  en terminal interactiva (detectado por `isatty()`).

## Reutilización de recursos

- Comparte un único `httpx.AsyncClient` entre adaptadores HTTP cuando sea
  posible. Si un adaptador puede recibir un cliente inyectado, permítelo vía
  parámetro opcional en `__init__` y cierra con `aclose()` solo el cliente que
  creó internamente.

## Calidad

- Antes de cada push: `./scripts/pre-push.sh` ejecuta `ruff` (lint + fix),
  `pyright` (tipos), `compileall` y `unittest`. Mantén el pipeline en verde.
