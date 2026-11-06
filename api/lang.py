"""Langue de l'interface (fr ou en) : lecture de l'en-tête et textes à deux versions."""

from contextvars import ContextVar
from typing import Literal

Lang = Literal["fr", "en"]

DEFAULT_LANG: Lang = "fr"
LANG_HEADER = "X-Lang"

_current: ContextVar[Lang] = ContextVar("lang", default=DEFAULT_LANG)


def parse_lang(raw: str | None) -> Lang:
    """Langue demandée par l'en-tête ; toute valeur inconnue donne le français."""
    return "en" if raw == "en" else DEFAULT_LANG


def set_lang(lang: Lang) -> None:
    """Fixe la langue de la requête en cours."""
    _current.set(lang)


def current_lang() -> Lang:
    """Langue de la requête en cours (français hors requête)."""
    return _current.get()


def msg(fr: str, en: str) -> str:
    """Retourne le message dans la langue de la requête en cours."""
    return en if current_lang() == "en" else fr
