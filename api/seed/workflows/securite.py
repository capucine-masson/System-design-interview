"""Catégorie Sécurité et gouvernance : hybride, chiffrement, offloading, rôles."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import graph
from api.seed.workflows.common import CONCEPTS, SOURCE, doc

ENCRYPTION = doc("/studio/workflows/building-workflows/encryption")
OFFLOADING = doc("/studio/workflows/building-workflows/payload_offloading")
ROLES = doc("/admin/identity-access/roles-permissions")

THEME = ThemeContent(
    slug="securite",
    titre="Sécurité et gouvernance",
    source_label=SOURCE,
    source_url=CONCEPTS,
    cards=[
        CardContent(
            titre="Architecture hybride",
            essentielle=True,
            accroche=(
                "Les données et le code restent chez le client. Mistral héberge seulement "
                "l'orchestration."
            ),
            points=[
                "Votre code de workflow et d'activity tourne dans votre environnement.",
                "L'orchestrateur, hébergé par Mistral, dispatche les tâches.",
                "L'orchestrateur ne détient jamais le code client.",
                "Argument fort pour les clients réglementés.",
            ],
            source_label=SOURCE,
            source_url=CONCEPTS,
            diagram=graph(
                [
                    ("m", "Orchestrateur (Mistral)", 0, 0),
                    ("c", "Workers (chez le client)", 1, 0),
                    ("d", "Données du client", 1, 1),
                ],
                [("m", "c", "tâches"), ("c", "d")],
            ),
        ),
        CardContent(
            titre="Chiffrement des payloads",
            essentielle=True,
            accroche=(
                "Le SDK chiffre les données avant qu'elles quittent le worker. La plateforme "
                "ne voit que du chiffré."
            ),
            points=[
                "Algorithme AES-GCM, clé de 256 bits, dans le SDK.",
                "Mode full : tout est chiffré (TEMPORAL_PAYLOAD_ENCRYPTION__MODE=full).",
                "Mode partiel : seuls les champs typés EncryptedStrField sont chiffrés.",
                "Rotation de clé possible avec une clé secondaire.",
            ],
            source_label=SOURCE,
            source_url=ENCRYPTION,
        ),
        CardContent(
            titre="Offloading des gros payloads",
            accroche=(
                "Au-delà de 2 Mo, les données partent dans le stockage objet du client plutôt "
                "que dans l'historique."
            ),
            points=[
                "Le SDK déporte automatiquement tout payload au-dessus de 2 Mo.",
                "Stockages supportés : AWS S3, Google Cloud Storage et Azure.",
                "Pas de suppression automatique : prévoir une règle de rétention du bucket.",
                "Au replay, les payloads sont retéléchargés : ça coûte du temps et du réseau.",
            ],
            source_label=SOURCE,
            source_url=OFFLOADING,
        ),
        CardContent(
            titre="Les rôles dans un workspace",
            accroche=(
                "Quatre rôles principaux : Developer, Workspace Contributor, Admin et "
                "Observability Viewer."
            ),
            points=[
                "Developer : construit et déploie.",
                "Workspace Contributor : contribue, sans traces ni évaluations live.",
                "Admin : administre le workspace.",
                "Observability Viewer : tout ce que fait un Developer, plus les traces et les "
                "évaluations live.",
            ],
            source_label=SOURCE,
            source_url=ROLES,
        ),
        CardContent(
            titre="Service accounts et secrets",
            accroche=(
                "Les workers de production utilisent un service account, pas un compte "
                "personnel. Les secrets sont en écriture seule."
            ),
            points=[
                "Un service account est limité à un workspace.",
                "Le rôle workflow_executor permet d'enregistrer et d'exécuter des workflows.",
                "Un secret ne peut plus être relu après sa création : écriture seule.",
                "Créer ou modifier un secret demande le rôle Developer.",
            ],
            source_label=SOURCE,
            source_url=doc("/admin/identity-access/service-accounts"),
        ),
    ],
)
