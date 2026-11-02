"""Catalogue des types de cas de system design : ajouter un cas = ajouter une entrée ici."""

from pydantic import BaseModel


class CaseType(BaseModel):
    """Un type de cas proposé au candidat."""

    slug: str
    titre: str
    description: str
    axes: list[str]


CASE_TYPES: list[CaseType] = [
    CaseType(
        slug="rag",
        titre="RAG sur une grande base documentaire",
        description="Répondre à des questions sur un très grand corpus de documents internes.",
        axes=[
            "volume et mise à jour des documents",
            "chunking et embeddings",
            "base vectorielle et reranking",
            "évaluation du retrieval",
            "hallucinations et citations",
            "droits d'accès",
        ],
    ),
    CaseType(
        slug="inference",
        titre="Service d'inférence LLM à grande échelle",
        description="Servir un LLM à beaucoup d'utilisateurs, avec latence et coût contraints.",
        axes=[
            "trafic et pics de charge",
            "latence au premier token contre débit",
            "GPU, batching continu, KV cache",
            "quantization",
            "autoscaling et streaming",
            "coût par token",
        ],
    ),
    CaseType(
        slug="entrainement",
        titre="Pipeline d'entraînement ou de fine-tuning",
        description="Entraîner ou adapter un modèle sur des données propriétaires.",
        axes=[
            "collecte, nettoyage et déduplication des données",
            "taille du modèle et budget de calcul",
            "parallélisme data, tensor, pipeline",
            "checkpointing et reprise sur panne",
            "LoRA contre full fine-tuning",
            "évaluation avant déploiement",
        ],
    ),
    CaseType(
        slug="evaluation",
        titre="Plateforme d'évaluation de LLM",
        description="Mesurer de façon fiable la qualité de modèles et de prompts en continu.",
        axes=[
            "benchmarks et jeux de test internes",
            "LLM-as-judge et sa validation",
            "évaluation humaine",
            "détection de régressions",
            "A/B tests en production",
            "coût et fréquence des évaluations",
        ],
    ),
    CaseType(
        slug="agent",
        titre="Agent ou assistant avec outils",
        description="Un assistant qui planifie et appelle des outils pour accomplir des tâches.",
        axes=[
            "outils et permissions",
            "mémoire et contexte",
            "garde-fous et actions irréversibles",
            "fiabilité sur plusieurs étapes",
            "observabilité et évaluation",
            "latence et coût par tâche",
        ],
    ),
    CaseType(
        slug="recommandation",
        titre="Recommandation ou modération avec ML",
        description="Un système ML qui classe ou filtre du contenu en continu.",
        axes=[
            "volume d'événements et latence de décision",
            "feature store et données en ligne/hors ligne",
            "entraînement et déploiement des modèles",
            "monitoring et dérive des données",
            "faux positifs, équité et boucle humaine",
            "démarrage à froid",
        ],
    ),
]


def get_case_type(slug: str) -> CaseType | None:
    """Retourne le type de cas correspondant au slug, s'il existe."""
    return next((case_type for case_type in CASE_TYPES if case_type.slug == slug), None)
