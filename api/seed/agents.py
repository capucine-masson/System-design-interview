"""Contenu du thème Agents (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

SOURCE = "LLM Powered Autonomous Agents (Lilian Weng, 2023)"

THEME = ThemeContent(
    slug="agents",
    titre="Agents",
    source_label=SOURCE,
    source_url="https://lilianweng.github.io/posts/2023-06-23-agent/",
    cards=[
        CardContent(
            titre="Qu'est-ce qu'un agent LLM ?",
            essentielle=True,
            accroche=(
                "Un agent, c'est un LLM utilisé comme contrôleur : il décide des "
                "actions à faire, appelle des outils et boucle jusqu'à atteindre l'objectif."
            ),
            points=[
                "Trois briques autour du modèle : la planification (décomposer et "
                "réviser), la mémoire (court et long terme), les outils (API, code, recherche).",
                "Différence avec un simple appel de LLM : le modèle choisit lui-même "
                "la suite des étapes, au lieu de suivre un enchaînement écrit à l'avance.",
                "Cela donne de la flexibilité, mais aussi moins de prévisibilité, "
                "plus de coût et plus de façons d'échouer.",
                "Exemples : assistant qui cherche et lit des pages, agent de code qui "
                "lance les tests, agent de support qui consulte un CRM.",
            ],
            source_label=SOURCE,
            diagram=graph(
                [
                    ("p", "Planification", 0, 0),
                    ("l", "LLM (contrôleur)", 1, 1),
                    ("m", "Mémoire", 2, 0),
                    ("o", "Outils", 2, 2),
                ],
                [("l", "p"), ("l", "m"), ("l", "o")],
            ),
        ),
        CardContent(
            titre="Planification et décomposition",
            accroche=(
                "Pour une tâche complexe, l'agent la découpe en sous-tâches et "
                "les traite dans l'ordre."
            ),
            points=[
                "Chain-of-thought : demander au modèle de réfléchir étape par étape "
                "donne une première forme de plan.",
                "Tree of thoughts : explorer plusieurs pistes et évaluer laquelle "
                "poursuivre, utile quand il faut revenir en arrière.",
                "Plan complet d'abord ou plan révisé au fur et à mesure : le "
                "second s'adapte aux surprises, le premier est plus lisible et économe.",
                "Un séparateur planificateur / exécutant permet d'utiliser un "
                "modèle fort pour planifier et un modèle moins cher pour exécuter.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Réflexion : ReAct et Reflexion",
            accroche=(
                "L'agent alterne réflexion et action, puis apprend de ses erreurs en les relisant."
            ),
            points=[
                "ReAct entrelace des étapes « pensée », « action » et « observation » : "
                "le raisonnement guide l'outil, le résultat de l'outil nourrit le suivant.",
                "Reflexion ajoute une auto-critique : quand une tentative échoue, "
                "l'agent écrit ce qui n'a pas marché et le garde en mémoire pour réessayer.",
                "Le signal d'échec doit être fiable (test qui échoue, erreur d'API) ; "
                "une auto-critique sans signal externe corrige mal.",
                "Il faut plafonner le nombre d'essais pour éviter de boucler.",
            ],
            source_label=SOURCE,
            diagram=flow(["Pensée", "Action (outil)", "Observation", "Nouvelle pensée"]),
        ),
        CardContent(
            titre="Mémoire",
            accroche=(
                "La mémoire d'un agent se joue à deux niveaux : le contexte actuel, "
                "limité, et un stockage externe consultable."
            ),
            points=[
                "Court terme : ce qui tient dans la fenêtre de contexte (historique, "
                "résultats d'outils) ; elle est finie et coûte des tokens.",
                "Long terme : un stockage externe, souvent une base vectorielle, "
                "interrogé par similarité pour retrouver les souvenirs utiles.",
                "Tactiques pour ne pas saturer le contexte : résumer l'historique, "
                "ne garder que les résultats utiles, tronquer les sorties d'outils.",
                "Attention à ce qu'on mémorise : des données erronées ou sensibles "
                "stockées durablement posent des problèmes de qualité et de confidentialité.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Utilisation d'outils",
            accroche=(
                "Les outils étendent ce que le modèle sait faire de façon fiable : "
                "calcul exact, données à jour, actions réelles."
            ),
            points=[
                "Le function calling : on décrit chaque outil (nom, rôle, schéma JSON "
                "des arguments) et le modèle produit un appel structuré.",
                "La qualité des descriptions d'outils compte autant que celle du "
                "prompt : un nom ou une description floue mène à de mauvais appels.",
                "Le code exécute l'outil et renvoie le résultat ; il valide "
                "toujours les arguments, car la sortie du modèle n'est jamais fiable.",
                "Moins d'outils, bien distincts, vaut mieux que beaucoup d'outils "
                "qui se recouvrent.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="La boucle de contrôle",
            essentielle=True,
            accroche=(
                "Au cœur d'un agent, il y a une boucle observer, décider, agir, qu'il faut borner."
            ),
            points=[
                "À chaque tour, le modèle voit l'état courant et choisit : appeler "
                "un outil ou répondre à l'utilisateur.",
                "Il faut un critère d'arrêt clair : objectif atteint, nombre maximal "
                "d'itérations, budget de tokens ou de temps épuisé.",
                "Détecter les boucles : mêmes actions répétées, absence de progrès ; "
                "dans ce cas, on arrête ou on passe la main à un humain.",
                "Tout est journalisé (trace complète) pour pouvoir rejouer et déboguer.",
            ],
            source_label=SOURCE,
            diagram=graph(
                [
                    ("s", "État", 0, 0),
                    ("d", "LLM décide", 1, 0),
                    ("a", "Outil / réponse", 2, 0),
                ],
                [("s", "d"), ("d", "a"), ("a", "s", "observation")],
            ),
        ),
        CardContent(
            titre="Garde-fous et sécurité",
            essentielle=True,
            accroche=(
                "Plus l'agent peut agir, plus il faut encadrer ce qu'il a le droit de faire."
            ),
            points=[
                "Moindre privilège : des outils en lecture seule par défaut, des "
                "permissions limitées, un bac à sable pour exécuter du code.",
                "Confirmation humaine avant toute action irréversible : "
                "suppression, paiement, envoi d'un message.",
                "Le contenu récupéré par les outils (pages web, documents, emails) "
                "peut contenir des instructions malveillantes : c'est de la donnée, "
                "jamais des ordres (injection de prompt).",
                "Validation des arguments, limites de débit et de coût, et liste "
                "d'actions autorisées plutôt qu'interdites.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Fiabilité : les erreurs s'accumulent",
            accroche=(
                "Sur plusieurs étapes, les petits taux d'erreur se multiplient : "
                "un agent peut échouer souvent même si chaque étape est bonne."
            ),
            points=[
                "Calcul à citer : 10 étapes à 95 % de réussite chacune donnent "
                "environ 60 % de réussite globale (0,95 puissance 10).",
                "Donc : réduire le nombre d'étapes, rendre chaque étape plus "
                "fiable, ajouter des vérifications entre les étapes.",
                "Les limites propres aux LLM s'ajoutent : contexte fini, planification "
                "fragile sur le long terme, format de sortie parfois invalide.",
                "On prévoit toujours un chemin de repli : réessayer, simplifier, "
                "ou escalader vers un humain.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Évaluer et observer un agent",
            accroche=(
                "On ne juge pas seulement la réponse finale, mais toute la "
                "trajectoire : outils choisis, arguments, nombre d'étapes."
            ),
            points=[
                "Journaliser chaque pensée, appel d'outil et résultat pour "
                "rejouer une exécution et trouver où elle a déraillé.",
                "Mesurer le taux de réussite de la tâche, mais aussi le nombre "
                "d'étapes, la latence et le coût par tâche.",
                "Évaluer séparément le choix d'outil et l'extraction des arguments : "
                "ce sont des échecs fréquents et faciles à tester.",
                "Alimenter le jeu de test avec les échecs réels rencontrés en production.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Agent ou workflow ?",
            essentielle=True,
            accroche=(
                "Avant de construire un agent, je me demande si un enchaînement "
                "d'étapes fixe ne suffirait pas."
            ),
            points=[
                "Workflow : les étapes sont écrites à l'avance, le LLM remplit "
                "chacune ; prévisible, testable, moins cher.",
                "Agent : le modèle choisit les étapes ; adapté aux tâches ouvertes "
                "dont on ne peut pas prévoir le chemin.",
                "Règle pratique : commencer par l'approche la plus simple (un appel), "
                "puis un workflow, et n'ajouter de l'autonomie que si on a mesuré le besoin.",
                "En entretien : expliquer ce compromis flexibilité contre contrôle "
                "montre un bon jugement d'ingénierie.",
            ],
            source_label=SOURCE,
        ),
    ],
)
