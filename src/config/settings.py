import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    groq_api_key: str
    deepseek_api_key: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        def _get(name: str) -> str:
            value = os.getenv(name, "").strip()
            if not value:
                raise ValueError(
                    f"Falta la variable de entorno obligatoria '{name}'. "
                    "Configúrala en el archivo .env o en el entorno."
                )
            return value

        return cls(
            telegram_bot_token=_get("TELEGRAM_BOT_TOKEN"),
            groq_api_key=_get("GROQ_API_KEY"),
            deepseek_api_key=_get("DEEPSEEK_API_KEY"),
        )
