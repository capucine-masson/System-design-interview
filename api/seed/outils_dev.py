"""Contenu du thème Outils du quotidien (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow

GIT = "Git Crash Course for Beginners (brandon1024, GitHub Gist)"
GIT_URL = "https://gist.github.com/brandon1024/14b5f9fcfd982658d01811ee3045ff1e"
PRECOMMIT = "Documentation pre-commit"
PRECOMMIT_URL = "https://pre-commit.com/"
IDE = "PyCharm vs VSCode (Tangent Technologies, 2020)"
IDE_URL = "https://tangenttechnologies.ca/blog/pycharm-vs-vscode/"
POSTMAN = "How to Use an API with Postman (freeCodeCamp, 2023)"
POSTMAN_URL = "https://www.freecodecamp.org/news/how-to-use-an-api-with-postman/"

THEME = ThemeContent(
    slug="outils-dev",
    titre="Outils du quotidien",
    source_label="Sources indiquées sur chaque carte",
    source_url=None,
    cards=[
        CardContent(
            titre="Git : les quatre zones d'un dépôt",
            essentielle=True,
            accroche=(
                "Git déplace le code entre quatre zones : le répertoire de travail, "
                "l'index, le dépôt local et le dépôt distant."
            ),
            points=[
                "Workspace : vos fichiers en cours de modification. git add les place dans "
                "l'index (staging), la liste de ce qui sera commité.",
                "git commit enregistre l'index dans le dépôt local ; git push l'envoie au "
                "dépôt distant ; git pull (fetch plus intégration) le rapatrie.",
                "git status avant un git add . évite d'embarquer des fichiers par erreur ; "
                "git log --oneline --graph montre l'historique.",
                "Configuration de départ : git config --global user.name et user.email.",
            ],
            source_label=GIT,
            source_url=GIT_URL,
            diagram=flow(["Workspace", "Index", "Dépôt local", "Dépôt distant"]),
        ),
        CardContent(
            titre="Git : branches, merge et rebase",
            essentielle=True,
            accroche=(
                "On travaille sur une branche par fonctionnalité, puis on l'intègre à la "
                "branche principale par merge ou par rebase."
            ),
            points=[
                "git checkout -b ma-feature crée et bascule sur une branche ; git branch "
                "liste, -d supprime une branche déjà fusionnée.",
                "Merge crée un commit de fusion et garde l'historique tel quel ; rebase "
                "rejoue vos commits au sommet de la branche cible pour un historique linéaire.",
                "Règle d'or du rebase : ne pas réécrire des commits déjà partagés ; le choix "
                "dépend des pratiques de l'équipe.",
                "Git-Flow est une convention de branches (master, staging, develop et "
                "branches de fonctionnalité).",
            ],
            source_label=GIT,
            source_url=GIT_URL,
        ),
        CardContent(
            titre="Git : mettre de côté et annuler",
            accroche=(
                "stash met un travail de côté, reset recule dans l'historique : utiles, mais "
                "reset --hard est destructif."
            ),
            points=[
                "git stash range les modifications en cours ; git stash pop les ramène, "
                "pratique pour changer de branche en urgence.",
                "git reset --soft HEAD^ annule le dernier commit en gardant les "
                "modifications dans l'index ; --mixed (par défaut) les garde non indexées.",
                "git reset --hard efface aussi les modifications du répertoire de travail : "
                "irréversible.",
                "Éviter git push -f sur une branche partagée, sauf si l'on sait exactement "
                "ce que l'on réécrit.",
            ],
            source_label=GIT,
            source_url=GIT_URL,
        ),
        CardContent(
            titre="Pre-commit : des contrôles avant chaque commit",
            essentielle=True,
            accroche=(
                "pre-commit lance automatiquement des vérifications (formatage, lint, types) "
                "sur les fichiers modifiés avant d'accepter un commit."
            ),
            points=[
                "Un crochet Git (hook) pre-commit s'exécute à git commit ; si un contrôle "
                "échoue, le commit est refusé.",
                "Avantage : les erreurs bêtes (espaces, imports inutilisés, secrets) sont "
                "arrêtées avant la CI et avant la revue de code.",
                "Le framework pre-commit gère les crochets pour toute l'équipe, à partir "
                "d'un seul fichier versionné.",
                "Beaucoup de crochets corrigent seuls (formatage) : on relit le diff puis "
                "on relance le commit.",
            ],
            source_label=PRECOMMIT,
            source_url=PRECOMMIT_URL,
            diagram=flow(["git commit", "Hooks pre-commit", "Commit accepté ou refusé"]),
        ),
        CardContent(
            titre="Pre-commit : configurer et installer",
            accroche=(
                "On décrit les contrôles dans .pre-commit-config.yaml, on installe les "
                "crochets une fois, et tout le monde en profite."
            ),
            points=[
                "Le fichier .pre-commit-config.yaml liste des dépôts de crochets, avec une "
                "version figée (rev) et les identifiants des crochets voulus.",
                "pre-commit install branche les crochets dans le dépôt local ; chacun doit "
                "le faire une fois après un clone.",
                "pre-commit run --all-files lance tout sur l'ensemble du code, utile à "
                "l'ajout d'un nouveau contrôle ou en CI.",
                "Exemple à citer : ruff et mypy comme crochets, pour que le dépôt reste "
                "propre sans y penser.",
            ],
            source_label=PRECOMMIT,
            source_url=PRECOMMIT_URL,
        ),
        CardContent(
            titre="PyCharm ou VS Code ?",
            accroche=(
                "PyCharm est un IDE spécialisé Python, très complet ; VS Code est un éditeur "
                "léger et polyvalent, étendu par des plugins."
            ),
            points=[
                "PyCharm gagne sur le refactoring, la complétion, le débogage et l'intégration "
                "Git ; l'étude citée donne 33/35 contre 23/35 pour VS Code.",
                "VS Code démarre plus vite (environ 4 s contre 15 s) mais, dans ce test, "
                "consommait plus de mémoire (environ 895 Mo contre 550 Mo).",
                "VS Code reste le couteau suisse pour plusieurs langages ; PyCharm "
                "est le choix évident si l'on fait surtout du Python.",
                "Nuance : l'article date de 2020 et teste un projet très simple ; "
                "les deux outils ont beaucoup évolué depuis.",
            ],
            source_label=IDE,
            source_url=IDE_URL,
        ),
        CardContent(
            titre="Postman : tester une API à la main",
            essentielle=True,
            accroche=(
                "Postman est un client graphique pour envoyer des requêtes HTTP à une API "
                "et inspecter ses réponses sans écrire de code."
            ),
            points=[
                "Méthodes : GET lit, POST crée (corps JSON), PUT met à jour, DELETE supprime.",
                "On règle l'URL, les paramètres de requête (?category=books), les en-têtes "
                "et le corps (onglet Body, au format JSON).",
                "Authentification : clé d'API dans un en-tête (X-API-Key) ou jeton Bearer "
                "dans Authorization: Bearer <jeton>.",
                "Exemple à citer : appeler GET /health d'une API FastAPI pour vérifier "
                "qu'elle répond.",
            ],
            source_label=POSTMAN,
            source_url=POSTMAN_URL,
        ),
        CardContent(
            titre="Postman : collections et tests",
            accroche=(
                "On range les requêtes en collections, on ajoute des tests automatiques et "
                "on partage le tout avec l'équipe."
            ),
            points=[
                "Une collection regroupe des requêtes liées ; on peut l'exporter, "
                "l'importer et la partager.",
                "L'onglet Tests accepte du JavaScript : pm.test('OK', () => "
                "pm.response.to.have.status(200)).",
                "Les scripts pre-request préparent la requête (ajout d'un en-tête, "
                "calcul d'une valeur) avant son envoi.",
                "En cas d'échec, vérifier dans l'ordre : connexion, URL de l'endpoint, "
                "identifiants, structure de la requête.",
            ],
            source_label=POSTMAN,
            source_url=POSTMAN_URL,
        ),
    ],
)
