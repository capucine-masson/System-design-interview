"""Contenu du thème Raisonnement / thinking (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

SOURCE = "« Why We Think » (Lilian Weng, 2025)"

THEME = ThemeContent(
    slug="reasoning",
    titre="Raisonnement et « thinking »",
    source_label=SOURCE,
    source_url="https://lilianweng.github.io/posts/2025-05-01-thinking/",
    cards=[
        CardContent(
            titre="Pourquoi laisser le modèle réfléchir",
            accroche=(
                "Donner du temps de réflexion au modèle, c'est lui donner plus de "
                "calcul sur la question, comme un humain qui prend le temps de raisonner."
            ),
            points=[
                "Analogie : la pensée rapide (intuition) contre la pensée lente "
                "(raisonnement explicite) ; un LLM classique répond en un seul passage.",
                "Écrire des étapes intermédiaires ajoute des tokens, donc du "
                "calcul, avant la réponse finale.",
                "Le calcul peut s'adapter à la difficulté : peu de réflexion pour "
                "une question simple, beaucoup pour un problème de maths.",
                "Prix à payer : plus de latence et de tokens facturés par requête.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Test-time compute",
            essentielle=True,
            accroche=(
                "Le test-time compute, c'est dépenser du calcul à l'inférence pour "
                "améliorer la réponse, au lieu d'agrandir le modèle."
            ),
            points=[
                "Deux leviers pour améliorer un modèle : plus de calcul à "
                "l'entraînement, ou plus de calcul à chaque question.",
                "Formes principales : générer une longue chaîne de raisonnement, "
                "échantillonner plusieurs réponses, ou réviser sa réponse.",
                "Un modèle plus petit qui réfléchit longtemps peut égaler un "
                "plus gros sur certaines tâches, avec un coût déplacé vers l'inférence.",
                "Le gain a des rendements décroissants et dépend de la tâche : "
                "fort sur maths et code, faible sur de la mémoire factuelle.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Chain of thought comme calcul intermédiaire",
            accroche=(
                "Les tokens de raisonnement servent de mémoire de travail : le "
                "modèle écrit pour mieux calculer."
            ),
            points=[
                "Un transformer a une profondeur fixe : écrire des étapes lui permet "
                "de faire plus d'opérations séquentielles qu'en un seul passage.",
                "Le bénéfice est plus marqué avec des modèles de grande taille.",
                "Plus de tokens de réflexion améliorent la précision jusqu'à un "
                "plateau, au-delà duquel on paie sans gagner.",
                "On peut fixer un budget de réflexion pour contrôler coût et latence.",
            ],
            source_label=SOURCE,
            diagram=flow(["Question", "Tokens de réflexion", "Réponse"]),
        ),
        CardContent(
            titre="Échantillonnage parallèle",
            essentielle=True,
            accroche=("On génère plusieurs réponses candidates, puis on en choisit une."),
            points=[
                "Best-of-N : on tire N réponses et on garde celle que juge le "
                "mieux un vérificateur (tests, modèle de récompense).",
                "Vote majoritaire (self-consistency) : on garde la réponse la plus "
                "fréquente, utile quand la réponse finale est courte et comparable.",
                "Beam search : on garde plusieurs pistes partielles et on élimine les moins "
                "prometteuses.",
                "Facile à paralléliser et sans modification du modèle, mais le "
                "coût croît linéairement avec N.",
            ],
            source_label=SOURCE,
            diagram=graph(
                [
                    ("q", "Question", 0, 1),
                    ("a", "Réponse 1", 1, 0),
                    ("b", "Réponse 2", 1, 1),
                    ("c", "Réponse N", 1, 2),
                    ("s", "Vérificateur / vote", 2, 1),
                ],
                [("q", "a"), ("q", "b"), ("q", "c"), ("a", "s"), ("b", "s"), ("c", "s")],
            ),
        ),
        CardContent(
            titre="Révision séquentielle",
            accroche=(
                "Le modèle relit sa réponse et la corrige ; ça marche seulement "
                "s'il reçoit un vrai retour."
            ),
            points=[
                "Principe : réponse, critique, nouvelle réponse, éventuellement "
                "répété plusieurs fois.",
                "Sans retour externe, l'auto-correction est peu fiable : le modèle "
                "peut même abîmer une réponse déjà correcte.",
                "Avec un signal fiable (tests unitaires, résultat d'un outil, "
                "message d'erreur), la correction devient efficace.",
                "Règle : d'abord chercher un vérificateur externe, puis seulement "
                "demander au modèle de se corriger.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Apprentissage par renforcement pour raisonner",
            essentielle=True,
            accroche=(
                "On entraîne le modèle avec une récompense quand sa réponse finale "
                "est correcte, et il apprend seul à raisonner plus longuement."
            ),
            points=[
                "Domaines idéaux : ceux où la réponse est vérifiable automatiquement, "
                "comme les maths (réponse exacte) et le code (tests qui passent).",
                "DeepSeek-R1 est l'exemple de référence, entraîné avec un algorithme "
                "de type GRPO et des récompenses simples sur ces tâches.",
                "Des comportements apparaissent : se vérifier, essayer une autre "
                "approche, allonger la réflexion sur les problèmes durs.",
                "Limite : hors domaines vérifiables (rédaction, jugement), la "
                "récompense est plus difficile à définir.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Récompense de processus ou de résultat",
            accroche=(
                "On peut récompenser seulement la réponse finale, ou noter chaque "
                "étape du raisonnement."
            ),
            points=[
                "Récompense de résultat : simple, juge la réponse finale ; "
                "le signal est rare mais difficile à tromper.",
                "Récompense de processus : un modèle note chaque étape, utile pour "
                "guider une recherche et repérer l'erreur exacte.",
                "Mais définir une « bonne étape » est difficile, et les modèles "
                "de récompense sont exploitables (reward hacking).",
                "Pour cette raison, plusieurs travaux récents préfèrent des "
                "récompenses de résultat vérifiables.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Fidélité du raisonnement affiché",
            accroche=(
                "La chaîne de pensée affichée n'est pas toujours la vraie raison "
                "de la réponse du modèle."
            ),
            points=[
                "Des expériences montrent que le modèle peut être influencé par un "
                "indice sans le mentionner dans son raisonnement.",
                "Les modèles de raisonnement reconnaissent plus souvent ces "
                "influences que les modèles classiques, sans que ce soit garanti.",
                "Lire la chaîne de pensée aide à surveiller un modèle, mais ce "
                "n'est pas une preuve de ce qu'il fait réellement.",
                "Pénaliser trop directement un mauvais raisonnement peut pousser "
                "le modèle à le cacher plutôt qu'à se corriger.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Outils pour mieux raisonner",
            accroche=(
                "Pour les calculs et les faits, le modèle fait mieux en déléguant "
                "à un outil qu'en devinant."
            ),
            points=[
                "Interpréteur de code : le modèle écrit un programme et on "
                "l'exécute (approche de type PAL), pour un résultat exact.",
                "Recherche et API : ReAct alterne raisonnement et appels d'outils "
                "pour aller chercher une information à jour.",
                "Les modèles de raisonnement récents savent appeler des outils "
                "au milieu de leur réflexion.",
                "Le résultat de l'outil sert aussi de retour externe fiable pour "
                "corriger un raisonnement.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Quand payer pour la réflexion ?",
            essentielle=True,
            accroche=(
                "Un modèle qui réfléchit coûte plus cher et répond plus lentement : "
                "je le réserve aux tâches qui en profitent."
            ),
            points=[
                "À activer : maths, code, planification, analyses à plusieurs "
                "étapes, cas où une erreur coûte cher.",
                "À éviter : classification simple, extraction, réponses "
                "courtes et chat à faible latence, où la qualité ne bouge pas.",
                "Mesurer : comparer qualité, latence et coût avec et sans "
                "réflexion sur son propre jeu d'évaluation.",
                "Régler le budget de réflexion selon la difficulté, voire router "
                "les requêtes faciles vers un modèle plus simple.",
            ],
            source_label=SOURCE,
        ),
    ],
)
