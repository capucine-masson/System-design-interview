"""Catégorie Durable execution et déterminisme : le cœur technique."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow
from api.seed.workflows.common import SOURCE, doc

WORKFLOWS_PAGE = doc("/studio/workflows/concepts/workflows")

THEME = ThemeContent(
    slug="durable",
    titre="Durable execution et déterminisme",
    source_label=SOURCE,
    source_url=WORKFLOWS_PAGE,
    cards=[
        CardContent(
            titre="Durable execution : comment ça marche ?",
            essentielle=True,
            accroche=(
                "Chaque étape est enregistrée. Si le worker plante, un autre reprend et "
                "rejoue le code sans refaire le travail déjà fait."
            ),
            points=[
                "Chaque étape terminée est écrite dans l'historique de l'exécution.",
                "Au crash, un autre worker reprend le workflow.",
                "Il rejoue le code du workflow à partir de l'historique.",
                "Les activities déjà terminées ne sont pas ré-exécutées : on réutilise leur "
                "résultat.",
            ],
            source_label=SOURCE,
            source_url=WORKFLOWS_PAGE,
            diagram=flow(["Étape faite", "Crash du worker", "Autre worker", "Replay", "Reprise"]),
        ),
        CardContent(
            titre="Pourquoi le workflow doit être déterministe",
            essentielle=True,
            accroche=(
                "Au replay, le code doit refaire exactement le même plan. Sinon l'historique "
                "ne correspond plus."
            ),
            points=[
                "Rejouer le workflow doit produire les mêmes décisions dans le même ordre.",
                "Donc pas d'I/O, pas d'aléatoire, pas d'horloge directe dans le workflow.",
                "À la place : workflow.now(), workflow.uuid4() et workflow.random().",
                "Ils remplacent datetime.now(), uuid.uuid4() et random.random().",
            ],
            source_label=SOURCE,
            source_url=WORKFLOWS_PAGE,
        ),
        CardContent(
            titre="Les effets de bord vont dans les activities",
            accroche=(
                "Tout ce qui parle au monde extérieur se fait dans une activity, jamais "
                "directement dans le workflow."
            ),
            points=[
                "Appel d'API, base de données, fichier, email, appel LLM : une activity.",
                "Le workflow reste un simple plan, rejouable à l'identique.",
                "Le résultat de l'activity est stocké : au replay, on ne la relance pas.",
            ],
            source_label=SOURCE,
            source_url=WORKFLOWS_PAGE,
        ),
        CardContent(
            titre="Idempotence : pourquoi une activity doit l'être",
            essentielle=True,
            accroche=(
                "Une activity en échec peut être relancée après avoir déjà agi en partie. "
                "Elle doit supporter d'être exécutée deux fois."
            ),
            points=[
                "Une activity qui échoue est retentée, parfois après des effets partiels.",
                "Exemple : un paiement ou un email peut partir, puis l'activity plante.",
                "Idempotente = relancée, elle donne le même résultat sans doubler l'effet.",
                "Astuce courante : une clé d'idempotence unique envoyée au service appelé.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/building-workflows/activities/basics"),
        ),
        CardContent(
            titre="Les limites à connaître",
            essentielle=True,
            accroche=(
                "Trois chiffres à retenir : 2 Mo par appel, environ 51 200 événements "
                "d'historique, 1 heure de timeout par défaut."
            ),
            points=[
                "2 Mo maximum en entrée et en sortie d'un workflow ou d'une activity.",
                "Historique limité à environ 51 200 événements ou 50 Mo.",
                "Contre l'historique trop long : continue_as_new.",
                "execution_timeout vaut 1 heure par défaut : à régler pour les longs workflows.",
                "Au-delà de 2 Mo, on passe par l'offloading dans un stockage objet.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/concepts/events"),
        ),
    ],
)
