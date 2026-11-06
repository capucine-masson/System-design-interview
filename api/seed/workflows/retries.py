"""Catégorie Retries et erreurs : reprises automatiques et erreurs métier."""

from api.course_models import CardContent, ThemeContent
from api.seed.workflows.common import SOURCE, doc

ACTIVITIES = doc("/studio/workflows/building-workflows/activities/basics")

THEME = ThemeContent(
    slug="retries",
    titre="Retries et erreurs",
    source_label=SOURCE,
    source_url=ACTIVITIES,
    cards=[
        CardContent(
            titre="Configurer les retries d'une activity",
            essentielle=True,
            accroche=(
                "Tout se règle dans le décorateur @workflows.activity : nombre d'essais, "
                "délai entre essais, durée max, heartbeat."
            ),
            points=[
                "retry_policy_max_attempts : le nombre maximum d'essais.",
                "retry_policy_backoff_coefficient : 2.0 veut dire que le délai double à "
                "chaque essai.",
                "start_to_close_timeout : la durée maximale d'une activity.",
                "heartbeat_timeout : le délai maximal entre deux signes de vie.",
                "La doc recommande de toujours régler start_to_close_timeout.",
            ],
            source_label=SOURCE,
            source_url=ACTIVITIES,
        ),
        CardContent(
            titre="Heartbeat : surveiller les activities longues",
            accroche=(
                "Une activity longue envoie un signe de vie régulier. Sans signe dans le "
                "délai, elle est considérée en échec et retentée."
            ),
            points=[
                "Utile pour une activity qui dure longtemps (traitement de gros fichier).",
                "Sans heartbeat dans heartbeat_timeout, l'activity est considérée en échec.",
                "Elle est alors retentée selon la politique de retry.",
                "Non supporté pour les activities locales.",
            ],
            source_label=SOURCE,
            source_url=ACTIVITIES,
        ),
        CardContent(
            titre="Erreurs métier et erreurs inattendues",
            essentielle=True,
            accroche=(
                "Une erreur attendue se lève proprement avec un code. Une erreur inattendue "
                "remonte et la plateforme applique les retries."
            ),
            points=[
                "Erreur métier attendue : WorkflowsException avec un ErrorCode.",
                "WorkflowsException porte un message, un status (500 par défaut), un code et "
                "un type.",
                "Les codes sont rangés par famille : activity, workflow, worker, agent...",
                "Erreur inattendue : on laisse remonter, la plateforme retente.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/building-workflows/workflow_exception"),
        ),
        CardContent(
            titre="Valeurs par défaut des retries : non documentées",
            accroche=(
                "La doc ne donne pas les défauts de retry et de timeout. Il faut le dire "
                "franchement et les fixer soi-même."
            ),
            points=[
                "Aucune valeur par défaut documentée pour max_attempts ni backoff.",
                "Même chose pour start_to_close_timeout et heartbeat_timeout.",
                "Réponse honnête si on vous le demande : on les règle explicitement.",
                "Ne citez pas un chiffre de mémoire : il ne vient pas de la doc officielle.",
            ],
            source_label=SOURCE,
            source_url=ACTIVITIES,
        ),
        CardContent(
            titre="Retry et idempotence vont ensemble",
            accroche=(
                "Les retries sont sûrs seulement si l'activity est idempotente. Sinon une "
                "reprise peut doubler un effet."
            ),
            points=[
                "Un retry relance l'activity depuis le début.",
                "Si elle avait déjà débité ou envoyé, l'effet peut être doublé.",
                "Donc : clé d'idempotence, ou vérifier l'état avant d'agir.",
                "À dire au client dès qu'une activity touche un paiement ou un email.",
            ],
            source_label=SOURCE,
            source_url=ACTIVITIES,
        ),
    ],
)
