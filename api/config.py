"""Configuration de l'application, lue depuis le `.env` racine."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env", override=False)


class ConfigError(RuntimeError):
    """Variable de configuration absente ou invalide."""


def _required(name: str) -> str:
    """Retourne la variable d'environnement ou lève une erreur claire."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"Variable manquante dans .env : {name}")
    return value


def _required_number(name: str) -> float:
    """Retourne la variable numérique requise."""
    raw = _required(name)
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} doit être un nombre (reçu : {raw!r})") from exc


@dataclass(frozen=True)
class Settings:
    """Paramètres de l'application."""

    api_port: int
    front_port: int
    db_path: Path
    mistral_api_key: str
    mistral_model: str
    price_input_per_m: float
    price_output_per_m: float
    llm_max_tokens: int
    llm_timeout_s: float

    @property
    def cors_origin(self) -> str:
        """Origine autorisée pour CORS (le front)."""
        return f"http://localhost:{self.front_port}"


def load_settings() -> Settings:
    """Construit les paramètres ; échoue si une variable est absente."""
    db_path = Path(_required("DB_PATH"))
    return Settings(
        api_port=int(_required_number("API_PORT")),
        front_port=int(_required_number("FRONT_PORT")),
        db_path=db_path if db_path.is_absolute() else ROOT_DIR / db_path,
        mistral_api_key=_required("MISTRAL_API_KEY"),
        mistral_model=_required("MISTRAL_MODEL"),
        price_input_per_m=_required_number("MISTRAL_PRICE_INPUT_PER_M"),
        price_output_per_m=_required_number("MISTRAL_PRICE_OUTPUT_PER_M"),
        llm_max_tokens=int(_required_number("LLM_MAX_TOKENS")),
        llm_timeout_s=_required_number("LLM_TIMEOUT_S"),
    )
