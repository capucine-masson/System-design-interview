"""Contenu de la section Mistral Workflows : un module par catégorie."""

from api.course_models import ThemeContent
from api.seed.workflows import (
    agents,
    concepts,
    declenchement,
    deploiement,
    durable,
    fde,
    interaction,
    observabilite,
    orchestration,
    positionnement,
    retries,
    securite,
)

THEMES: tuple[ThemeContent, ...] = (
    positionnement.THEME,
    concepts.THEME,
    durable.THEME,
    retries.THEME,
    interaction.THEME,
    orchestration.THEME,
    agents.THEME,
    declenchement.THEME,
    deploiement.THEME,
    securite.THEME,
    observabilite.THEME,
    fde.THEME,
)
