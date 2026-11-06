"""Traductions anglaises du cours : un module par thème, même ordre de cartes que le français."""

from api.course_models import ThemeTranslation
from api.seed.en import (
    agents,
    cicd_infra,
    ddia,
    evaluation,
    inference,
    outils_dev,
    prompting,
    python_donnees,
    python_execution,
    rag,
    reasoning,
    system_design,
    transformers,
)

TRANSLATIONS_EN: tuple[ThemeTranslation, ...] = (
    transformers.THEME,
    inference.THEME,
    evaluation.THEME,
    prompting.THEME,
    agents.THEME,
    reasoning.THEME,
    system_design.THEME,
    ddia.THEME,
    rag.THEME,
    python_donnees.THEME,
    python_execution.THEME,
    outils_dev.THEME,
    cicd_infra.THEME,
)
