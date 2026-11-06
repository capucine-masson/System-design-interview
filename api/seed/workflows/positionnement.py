"""Catégorie Positionnement : pourquoi Mistral Workflows existe et quand l'utiliser."""

from api.course_models import CardContent, ThemeContent
from api.seed.workflows.common import OVERVIEW, SOURCE, doc

THEME = ThemeContent(
    slug="positionnement",
    titre="Positionnement",
    source_label=SOURCE,
    source_url=OVERVIEW,
    cards=[
        CardContent(
            titre="C'est quoi Mistral Workflows ?",
            essentielle=True,
            accroche=(
                "C'est l'orchestration de Mistral Studio : elle fait tourner des processus IA "
                "en plusieurs étapes, sans perdre l'état si quelque chose plante."
            ),
            points=[
                "Elle est construite sur Temporal, un moteur open source d'exécution durable.",
                "Durable : chaque étape est enregistrée, un crash ne fait pas tout recommencer.",
                "Observable : on suit chaque exécution dans Mistral Studio.",
                "Tolérante aux pannes : une étape qui échoue peut être retentée.",
                "Elle est en public preview : le produit évolue encore.",
            ],
            source_label=SOURCE,
            source_url=OVERVIEW,
        ),
        CardContent(
            titre="Le problème résolu : du POC à la production",
            essentielle=True,
            accroche=(
                "Un POC enchaîne des appels dans un script. En production, ce script ne tient "
                "pas : il perd son état au premier crash."
            ),
            points=[
                "Un script qui enchaîne LLM, API et validation humaine perd tout s'il plante.",
                "Il n'a ni retries propres, ni historique d'audit.",
                "Il ne peut pas attendre une validation humaine pendant plusieurs jours.",
                "Workflows apporte l'état durable, les reprises, la trace et la pause longue.",
            ],
            source_label=SOURCE,
            source_url=OVERVIEW,
        ),
        CardContent(
            titre="Pourquoi pas Celery, une queue ou un cron ?",
            accroche=(
                "Une queue ou un cron lancent des tâches, mais ne gardent pas l'état d'un "
                "processus entier. Il faudrait tout recoder soi-même."
            ),
            points=[
                "Il faudrait recoder l'état du processus entre les étapes.",
                "Il faudrait recoder les reprises après erreur et les timeouts.",
                "Il faudrait construire soi-même l'historique de ce qui s'est passé.",
                "Avec Workflows, ces briques sont fournies par la plateforme.",
            ],
            source_label=SOURCE,
            source_url=OVERVIEW,
        ),
        CardContent(
            titre="Pourquoi pas Temporal seul ?",
            accroche=(
                "Mistral utilise Temporal pour la durabilité, puis ajoute ce qui manque pour "
                "des produits IA en entreprise."
            ),
            points=[
                "Le moteur durable vient de Temporal (la doc le dit explicitement).",
                "Mistral ajoute le streaming et la gestion des gros payloads.",
                "Il ajoute le multi-tenant et l'interface Studio.",
                "Il ajoute l'intégration agents et LLM.",
                "Il ajoute la gouvernance : rôles (RBAC) et secrets.",
            ],
            source_label=SOURCE,
            source_url=OVERVIEW,
        ),
        CardContent(
            titre="Workflow ou agent : quelle différence ?",
            essentielle=True,
            accroche=(
                "Le workflow est un processus codé à l'avance, prévisible. L'agent décide "
                "lui-même de la suite. On peut mettre un agent dans un workflow."
            ),
            points=[
                "Workflow : un code qui décide quoi faire et dans quel ordre, de façon "
                "déterministe.",
                "Agent : un LLM qui choisit dynamiquement ses outils et ses étapes.",
                "Un workflow peut contenir des agents : le cadre est fixe, l'agent est un "
                "composant.",
                "Règle simple : processus connu à l'avance, workflow ; tâche ouverte, agent.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/concepts/workflows"),
        ),
        CardContent(
            titre="Quand ne pas l'utiliser ?",
            accroche=(
                "Pour un simple appel LLM sans enchaînement ni attente, l'orchestration "
                "ajoute de la complexité pour rien."
            ),
            points=[
                "Un seul appel LLM, sans étapes, sans reprise : un appel direct suffit.",
                "Pas de besoin de durabilité, d'audit ni de validation humaine : inutile.",
                "L'orchestration vaut le coup quand le processus a plusieurs étapes qui "
                "peuvent échouer ou durer longtemps.",
            ],
            source_label=SOURCE,
            source_url=OVERVIEW,
        ),
        CardContent(
            titre="Cas d'usage typiques",
            accroche=(
                "Les processus qui mélangent IA, règles métier et validation humaine : "
                "conformité, douane, support."
            ),
            points=[
                "KYC et conformité : extraction, contrôles, validation d'un humain.",
                "Douane et cargo : lire des documents, vérifier, décider.",
                "Triage de tickets : classer, router, escalader.",
                "Clients cités par Mistral : ASML, La Banque Postale, CMA-CGM, France Travail.",
            ],
            source_label=SOURCE,
            source_url=OVERVIEW,
        ),
    ],
)
