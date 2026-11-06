"""Catégorie Interagir avec un workflow en cours : signal, query, update, attente."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import graph
from api.seed.workflows.common import SOURCE, doc

SIGNALS = doc("/studio/workflows/interacting-with-workflows/signals")
WAIT = doc("/studio/workflows/building-workflows/waiting_for_conditions")

THEME = ThemeContent(
    slug="interaction",
    titre="Interagir avec un workflow en cours",
    source_label=SOURCE,
    source_url=SIGNALS,
    cards=[
        CardContent(
            titre="Signal, query, update : trois façons de parler",
            essentielle=True,
            accroche=(
                "Pour parler à un workflow qui tourne : le signal écrit sans réponse, la "
                "query lit, l'update écrit et répond."
            ),
            points=[
                "Signal : un message asynchrone qui modifie l'état, ne renvoie rien.",
                "Query : lecture seule, synchrone, rapide, renvoie une valeur.",
                "Update : modifie l'état, renvoie une valeur, peut lancer des activities.",
                "Exemple : signal pour approuver, query pour lire l'avancement.",
            ],
            source_label=SOURCE,
            source_url=SIGNALS,
        ),
        CardContent(
            titre="Attendre sans rien consommer : wait_condition",
            essentielle=True,
            accroche=(
                "workflow.wait_condition suspend le workflow jusqu'à ce qu'une condition soit "
                "vraie, sans coût de calcul pendant l'attente."
            ),
            points=[
                "Exemple : workflow.wait_condition(lambda: self.approved, timeout=...).",
                "Le workflow dort jusqu'à ce que la condition devienne vraie.",
                "Avec un timeout, une asyncio.TimeoutError est levée si le délai est dépassé.",
                "Toujours prévoir le timeout et la branche de refus ou d'escalade.",
            ],
            source_label=SOURCE,
            source_url=WAIT,
        ),
        CardContent(
            titre="Approbation humaine pas à pas",
            essentielle=True,
            accroche=(
                "Le workflow s'arrête et attend. Quand l'humain valide, un signal arrive et "
                "le workflow reprend."
            ),
            points=[
                "Le workflow fait ses étapes automatiques, puis attend avec wait_condition.",
                "Un humain décide dans une interface ; elle envoie un signal « approve ».",
                "Le signal change l'état, la condition devient vraie, le workflow reprend.",
                "Sans réponse avant le timeout : escalade ou refus par défaut.",
                "Tout est dans l'historique : qui a validé, et quand.",
            ],
            source_label=SOURCE,
            source_url=WAIT,
            diagram=graph(
                [
                    ("a", "Étapes automatiques", 0, 0),
                    ("w", "wait_condition", 1, 0),
                    ("r", "Reprise", 2, 0),
                    ("t", "Escalade / refus", 1, 1),
                ],
                [("a", "w"), ("w", "r", "signal approve"), ("w", "t", "timeout")],
            ),
        ),
        CardContent(
            titre="Signal ou update : comment choisir ?",
            accroche=(
                "Le signal suffit pour notifier. L'update est préférable quand l'appelant "
                "attend un résultat."
            ),
            points=[
                "Signal : « fire and forget », il ne retourne rien à l'appelant.",
                "Update : retourne une valeur et peut lancer des activities.",
                "Besoin de lire sans rien changer : query.",
            ],
            source_label=SOURCE,
            source_url=SIGNALS,
        ),
        CardContent(
            titre="Un chat : InteractiveWorkflow",
            accroche=(
                "Pour un workflow conversationnel, on étend InteractiveWorkflow et on attend "
                "le message suivant avec wait_for_input."
            ),
            points=[
                "La classe de base s'appelle InteractiveWorkflow.",
                "Le workflow appelle self.wait_for_input(...) avec un ChatInput.",
                "wait_for_input accepte un timeout optionnel.",
                "Le workflow reste en attente entre deux messages de l'utilisateur.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/interacting-with-workflows/conversational_workflows"),
        ),
    ],
)
