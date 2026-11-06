"""Catégorie Workers et déploiement : modes, worker, échelle, conflits de deployment."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import graph
from api.seed.workflows.common import SOURCE, doc

WORKERS = doc("/studio/workflows/concepts/workers")
PROD_DEPLOYMENTS = doc("/studio/workflows/managing-workflows-in-production/deployments")

THEME = ThemeContent(
    slug="deploiement",
    titre="Workers et déploiement",
    source_label=SOURCE,
    source_url=WORKERS,
    cards=[
        CardContent(
            titre="Où tournent les workers ?",
            essentielle=True,
            accroche=(
                "Deux modes dans la doc : self-hosted, sur votre infrastructure, ou managé, "
                "où Mistral construit et fait tourner le worker."
            ),
            points=[
                "Self-hosted : vos machines ou votre Kubernetes, y compris en dev local.",
                "Managé : Mistral Cloud construit et exécute le worker pour vous.",
                "Il n'y a pas de mode « local » nommé : le local est du self-hosted.",
                "Dans tous les cas, l'orchestrateur reste hébergé par Mistral.",
            ],
            source_label=SOURCE,
            source_url=WORKERS,
        ),
        CardContent(
            titre="Lancer un worker : run_worker",
            essentielle=True,
            accroche=(
                "On appelle run_worker avec la liste des workflows à gérer. Deux variables "
                "d'environnement décident où il se connecte."
            ),
            points=[
                "run_worker([...]) reçoit les classes de workflows que le worker gère.",
                "MISTRAL_API_KEY détermine à quel workspace le worker se connecte.",
                "DEPLOYMENT_NAME détermine le deployment qu'il rejoint.",
            ],
            source_label=SOURCE,
            source_url=WORKERS,
        ),
        CardContent(
            titre="Passer à l'échelle",
            accroche=(
                "Un worker ne garde pas d'état : on ajoute simplement des réplicas du même "
                "deployment."
            ),
            points=[
                "L'état est dans l'historique côté plateforme, pas dans le worker.",
                "Les workers sont donc interchangeables.",
                "Pour monter en charge : plus de réplicas, par exemple sur Kubernetes.",
                "Toutes les réplicas utilisent le même DEPLOYMENT_NAME.",
            ],
            source_label=SOURCE,
            source_url=WORKERS,
        ),
        CardContent(
            titre="Erreur 409 : deux deployments, même workflow",
            essentielle=True,
            accroche=(
                "Si deux deployments actifs exposent le même workflow, la plateforme ne sait "
                "pas où l'envoyer et répond 409."
            ),
            points=[
                "Le code d'erreur est AMBIGUOUS_WORKFLOW.",
                "Il survient seulement si les deux deployments sont actifs.",
                "Correction : préciser deployment_name au lancement.",
                "Un deployment inactif ne reçoit rien et ne compte pas dans le conflit.",
            ],
            source_label=SOURCE,
            source_url=PROD_DEPLOYMENTS,
            diagram=graph(
                [
                    ("c", "Appel : workflow X", 0, 1),
                    ("a", "Deployment A (actif)", 1, 0),
                    ("b", "Deployment B (actif)", 1, 2),
                ],
                [("c", "a", "?"), ("c", "b", "?")],
            ),
        ),
        CardContent(
            titre="Un deployment peut devenir inactif",
            accroche=(
                "Si les workers ne donnent plus signe de vie, le deployment devient inactif "
                "et ne reçoit plus d'exécutions."
            ),
            points=[
                "Les workers signalent régulièrement qu'ils sont vivants.",
                "Sans signe dans la fenêtre prévue, le deployment passe inactif.",
                "À vérifier en premier quand une exécution ne démarre pas.",
            ],
            source_label=SOURCE,
            source_url=PROD_DEPLOYMENTS,
        ),
        CardContent(
            titre="Tester en local sans voler les exécutions",
            accroche=(
                "Un worker de test doit avoir un DEPLOYMENT_NAME différent de celui de "
                "production, sinon il prend ses exécutions."
            ),
            points=[
                "Un worker local qui rejoint le deployment live se met à recevoir ses runs.",
                "Donner au worker de test un DEPLOYMENT_NAME distinct.",
                "Lancer ensuite en ciblant ce deployment avec deployment_name.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/managing-workflows-in-production/deployments"),
        ),
        CardContent(
            titre="Helm chart : non documenté",
            accroche=(
                "Le blog Mistral évoque un Helm chart, mais aucune page de doc ne le détaille. "
                "Ne pas l'affirmer."
            ),
            points=[
                "Rien dans la doc consultée sur un Helm chart officiel.",
                "Réponse honnête : « je ne l'ai pas vu documenté, je le vérifie ».",
                "Ce qui est documenté : des workers stateless, à répliquer sur Kubernetes.",
            ],
            source_label=SOURCE,
            source_url=WORKERS,
        ),
    ],
)
