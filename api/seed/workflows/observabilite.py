"""Catégorie Observabilité : Studio, OpenTelemetry, débogage d'une exécution bloquée."""

from api.course_models import CardContent, ThemeContent
from api.seed.workflows.common import SOURCE, doc

OBSERVABILITY = doc("/studio/workflows/observability")

THEME = ThemeContent(
    slug="observabilite",
    titre="Observabilité",
    source_label=SOURCE,
    source_url=OBSERVABILITY,
    cards=[
        CardContent(
            titre="Suivre une exécution dans Studio",
            essentielle=True,
            accroche=(
                "L'onglet Executions de Studio montre ce qui s'est passé dans chaque "
                "exécution : étapes, logs, traces."
            ),
            points=[
                "Chemin : Studio, Workflows, Executions.",
                "On y voit la timeline de l'exécution et les logs.",
                "Les traces donnent un span par activity.",
                "Utile pour l'audit comme pour le diagnostic.",
            ],
            source_label=SOURCE,
            source_url=OBSERVABILITY,
        ),
        CardContent(
            titre="OpenTelemetry : où vont les logs et traces",
            accroche=(
                "Le worker exporte par défaut ses logs, traces et métriques vers Studio, en "
                "OpenTelemetry."
            ),
            points=[
                "Export OpenTelemetry par défaut vers la plateforme Mistral.",
                "OTEL_ENDPOINT permet de rediriger vers un endpoint à soi.",
                "OTEL_ENABLED=false désactive la télémétrie.",
            ],
            source_label=SOURCE,
            source_url=OBSERVABILITY,
        ),
        CardContent(
            titre="Piège : rediriger les traces les fait disparaître de Studio",
            essentielle=True,
            accroche=(
                "Si on envoie logs et traces vers un endpoint personnalisé, Studio ne les "
                "reçoit plus."
            ),
            points=[
                "Rediriger avec OTEL_ENDPOINT envoie les signaux ailleurs.",
                "Studio n'affiche alors plus ces logs et traces.",
                "À signaler au client qui a déjà sa propre stack d'observabilité.",
            ],
            source_label=SOURCE,
            source_url=OBSERVABILITY,
        ),
        CardContent(
            titre="Débugger une exécution bloquée",
            essentielle=True,
            accroche=(
                "On suit une check-list : statut, historique, logs du worker, deployment "
                "actif, boucle de retry."
            ),
            points=[
                "Regarder le statut de l'exécution dans Studio.",
                "Lire l'historique d'événements : où s'est-elle arrêtée ?",
                "Lire les logs du worker concerné.",
                "Vérifier que le deployment est actif et qu'un worker est connecté.",
                "Chercher une activity qui boucle en retry.",
            ],
            source_label=SOURCE,
            source_url=OBSERVABILITY,
        ),
    ],
)
