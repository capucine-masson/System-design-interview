"""Constantes partagées par les fichiers de contenu Mistral Workflows."""

SOURCE = "Doc Mistral Workflows"
DOCS_BASE = "https://docs.mistral.ai"


def doc(path: str) -> str:
    """URL d'une page de la doc officielle à partir de son chemin."""
    return f"{DOCS_BASE}{path}"


OVERVIEW = doc("/studio/workflows/overview")
CONCEPTS = doc("/studio/workflows/concepts/overview")
