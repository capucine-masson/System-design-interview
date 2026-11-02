"""Contenu du thème Prompt engineering (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

SOURCE = "Prompt Engineering (Lilian Weng, 2023)"

THEME = ThemeContent(
    slug="prompt-engineering",
    titre="Prompt engineering",
    source_label=SOURCE,
    source_url="https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    cards=[
        CardContent(
            titre="Structurer un bon prompt",
            essentielle=True,
            accroche=(
                "Un bon prompt est une spécification : il dit la tâche, le contexte, "
                "le format attendu et ce qui est interdit."
            ),
            points=[
                "Éléments utiles : le rôle ou le public visé, la tâche précise, les "
                "contraintes, le format de sortie, un ou deux exemples.",
                "Être explicite plutôt que laisser deviner : « réponds en 3 puces de "
                "moins de 20 mots » vaut mieux que « sois concis ».",
                "Délimiter le contenu externe (balises, guillemets) pour séparer "
                "les instructions des données, ce qui réduit aussi l'injection de prompt.",
                "Le prompt se teste comme du code : on change une chose à la fois et on "
                "compare sur un jeu d'exemples.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Zero-shot et few-shot",
            essentielle=True,
            accroche=(
                "En zero-shot on décrit seulement la tâche ; en few-shot on ajoute "
                "quelques exemples entrée-sortie dans le prompt."
            ),
            points=[
                "Le few-shot apprend le format et le style par l'exemple, sans "
                "réentraîner le modèle : c'est de l'apprentissage en contexte.",
                "Il aide surtout quand la consigne seule est ambiguë ou le format "
                "inhabituel ; sur les modèles récents, le zero-shot suffit souvent.",
                "Coût : chaque exemple consomme des tokens à chaque appel, donc "
                "de la latence et de l'argent.",
                "Quelques exemples (3 à 5) suffisent en général ; au-delà, le gain diminue vite.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Choisir et ordonner les exemples",
            accroche=(
                "Les résultats d'un few-shot dépendent beaucoup de quels exemples on "
                "met et dans quel ordre."
            ),
            points=[
                "Choisir des exemples proches de la question (recherche par "
                "similarité d'embedding) donne souvent de meilleurs résultats que des exemples "
                "fixes.",
                "Biais connus : le modèle favorise l'étiquette majoritaire parmi "
                "les exemples et celle qui apparaît en dernier.",
                "Parades : équilibrer les classes, varier l'ordre, couvrir des cas "
                "variés plutôt que des exemples quasi identiques.",
                "On choisit sur un jeu de développement mesuré, pas à l'intuition.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Instructions et modèles instruct",
            accroche=(
                "Les modèles « instruct » sont entraînés à suivre des consignes ; "
                "il faut donc les écrire comme à un collègue compétent mais sans contexte."
            ),
            points=[
                "Décrire l'audience et l'objectif : expliquer à quel usage la "
                "sortie servira améliore le niveau de détail.",
                "Préférer dire quoi faire plutôt que quoi éviter, et donner les "
                "critères de réussite.",
                "Séparer le prompt système (règles stables) du message utilisateur "
                "(donnée variable).",
                "Pour une sortie machine, demander un format structuré et le "
                "valider derrière, car la sortie n'est jamais garantie.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Chain-of-thought",
            essentielle=True,
            accroche=(
                "Demander au modèle de raisonner étape par étape avant de répondre "
                "améliore souvent les tâches de logique et de calcul."
            ),
            points=[
                "Version few-shot : les exemples montrent le raisonnement complet "
                "avant la réponse ; version zero-shot : une simple consigne du type « réfléchis "
                "étape par étape ».",
                "Le gain est net sur l'arithmétique, la logique et le raisonnement "
                "à plusieurs sauts, surtout avec des modèles assez grands.",
                "Coût : plus de tokens générés, donc plus de latence et d'argent, "
                "et le raisonnement affiché n'est pas toujours fidèle.",
                "Les modèles « de raisonnement » récents font ce travail en interne : "
                "inutile alors de le demander explicitement.",
            ],
            source_label=SOURCE,
            diagram=flow(["Question", "Étapes de raisonnement", "Réponse finale"]),
        ),
        CardContent(
            titre="Self-consistency",
            essentielle=True,
            accroche=(
                "On génère plusieurs raisonnements indépendants et on garde la "
                "réponse la plus fréquente."
            ),
            points=[
                "On échantillonne N chaînes de pensée avec une température > 0, "
                "puis on fait un vote majoritaire sur la réponse finale.",
                "Intuition : les erreurs sont dispersées, la bonne réponse revient plus souvent.",
                "Gain réel sur le calcul et le raisonnement, mais le coût est "
                "multiplié par N (par exemple 5 à 10 appels).",
                "À réserver aux cas où l'erreur coûte cher et où la réponse est "
                "courte et comparable (un nombre, une classe).",
            ],
            source_label=SOURCE,
            diagram=graph(
                [
                    ("q", "Question", 0, 1),
                    ("a", "Chaîne 1", 1, 0),
                    ("b", "Chaîne 2", 1, 1),
                    ("c", "Chaîne N", 1, 2),
                    ("v", "Vote majoritaire", 2, 1),
                ],
                [
                    ("q", "a"),
                    ("q", "b"),
                    ("q", "c"),
                    ("a", "v"),
                    ("b", "v"),
                    ("c", "v"),
                ],
            ),
        ),
        CardContent(
            titre="Tree of Thoughts",
            accroche=(
                "Au lieu d'une seule chaîne, le modèle explore plusieurs pistes "
                "sous forme d'arbre et évalue chaque étape."
            ),
            points=[
                "À chaque étape, le modèle propose plusieurs « pensées » possibles, "
                "puis les note (prometteuse ou non).",
                "Un algorithme de recherche (largeur d'abord ou profondeur d'abord) "
                "choisit quelles branches développer ou abandonner.",
                "Utile pour les problèmes qui demandent d'anticiper ou de revenir "
                "en arrière (puzzles, planification).",
                "Très coûteux en appels : réservé à des tâches difficiles où "
                "une simple chaîne échoue.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Optimisation automatique de prompts",
            accroche=(
                "On peut utiliser un LLM pour proposer, tester et améliorer "
                "des prompts, à condition d'avoir une mesure."
            ),
            points=[
                "Principe : un modèle génère des variantes d'instruction, on les "
                "évalue sur un jeu d'exemples, on garde la meilleure et on recommence.",
                "Des approches comme APE automatisent cette boucle ; l'idée est de "
                "traiter le prompt comme un paramètre à optimiser.",
                "Sans métrique fiable, l'optimisation sur-ajuste ou dérive : les "
                "évals passent avant l'automatisation.",
                "Garder un jeu de test séparé pour vérifier que le gain est réel.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Prompt, outils et connaissances externes",
            accroche=(
                "Le prompt seul ne sait que ce que le modèle a appris : pour le "
                "reste, on lui donne du contexte ou des outils."
            ),
            points=[
                "Retrieval : on injecte des passages pertinents dans le prompt "
                "pour répondre avec des informations à jour ou privées.",
                "Outils : calculatrice, interpréteur de code, API, que le modèle "
                "appelle quand il en a besoin, pour ce qu'il fait mal (calcul exact).",
                "Sortie structurée : demander un JSON conforme à un schéma, "
                "puis le valider côté code.",
                "Tout contenu externe est de la donnée non fiable : jamais "
                "des instructions à exécuter.",
            ],
            source_label=SOURCE,
        ),
    ],
)
