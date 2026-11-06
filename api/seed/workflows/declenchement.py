"""Catégorie Déclenchement : API, schedules, webhooks et triggers."""

from api.course_models import CardContent, ThemeContent
from api.seed.workflows.common import SOURCE, doc

SCHEDULING = doc("/studio/workflows/building-workflows/scheduling")

THEME = ThemeContent(
    slug="declenchement",
    titre="Déclenchement",
    source_label=SOURCE,
    source_url=SCHEDULING,
    cards=[
        CardContent(
            titre="Comment lance-t-on un workflow ?",
            essentielle=True,
            accroche=(
                "Par l'API ou le SDK, depuis Studio, sur un événement externe, ou selon un "
                "planning."
            ),
            points=[
                "API : POST /v1/workflows/{name}/execute, depuis n'importe quel client.",
                "SDK : par exemple client.workflows.execute_workflow(...).",
                "Studio : lancement depuis l'interface.",
                "Webhooks et triggers : un événement d'un service tiers déclenche le workflow.",
                "Schedules : cron ou intervalle régulier.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio-api/workflows/getting-started/overview"),
        ),
        CardContent(
            titre="Schedules : lancer à heure fixe",
            accroche=(
                "Un schedule lance un workflow à intervalle ou selon un cron. Il est en UTC "
                "par défaut."
            ),
            points=[
                "Cron ou intervalle régulier.",
                "Fuseau horaire : UTC par défaut, réglable avec time_zone_name (nom IANA).",
                "On peut mettre un schedule en pause, puis le relancer.",
            ],
            source_label=SOURCE,
            source_url=SCHEDULING,
        ),
        CardContent(
            titre="Overlap policy : si le run précédent n'est pas fini",
            essentielle=True,
            accroche=(
                "L'overlap policy dit quoi faire quand un schedule se déclenche alors que le "
                "run précédent tourne encore. Par défaut : SKIP."
            ),
            points=[
                "SKIP (défaut) : le nouveau run est abandonné.",
                "BUFFER_ONE : on garde un seul run en attente.",
                "BUFFER_ALL : tous les runs sont mis en file.",
                "CANCEL_OTHER / TERMINATE_OTHER : on arrête l'ancien run.",
                "ALLOW_ALL : les runs tournent en parallèle.",
            ],
            source_label=SOURCE,
            source_url=SCHEDULING,
        ),
        CardContent(
            titre="Webhooks et triggers",
            accroche=(
                "Un webhook reçoit des événements d'un service tiers. Un trigger relie cet "
                "événement à un workflow à lancer."
            ),
            points=[
                "Webhook : un endpoint HTTP qui reçoit les événements d'un fournisseur.",
                "Trigger : la règle qui démarre un workflow quand l'événement arrive.",
                "Endpoints : POST /v1/webhooks et POST /v1/triggers.",
                "Supprimer un webhook encore utilisé par des triggers renvoie un 409.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/building-workflows/triggers-and-webhooks"),
        ),
    ],
)
