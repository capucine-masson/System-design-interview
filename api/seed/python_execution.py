"""Contenu du thème Python : exécution et qualité (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow

ASYNCIO = "Asyncio (Built In)"
ASYNCIO_URL = "https://builtin.com/data-science/asyncio"
LOGGING = "Python logging basics (Loggly)"
LOGGING_URL = "https://www.loggly.com/ultimate-guide/python-logging-basics/"
FIRE = "Python Fire (Google, GitHub)"
FIRE_URL = "https://github.com/google/python-fire"
MYPY = "mypy : Getting started (documentation officielle)"
MYPY_URL = "https://mypy.readthedocs.io/en/stable/getting_started.html"
UV = "Python UV (DataCamp)"
UV_URL = "https://www.datacamp.com/tutorial/python-uv"

THEME = ThemeContent(
    slug="python-execution",
    titre="Python : exécution et qualité",
    source_label="Sources indiquées sur chaque carte",
    source_url=None,
    cards=[
        CardContent(
            titre="Asyncio : async et await",
            essentielle=True,
            accroche=(
                "Asyncio permet de gérer beaucoup d'attentes (réseau, base, disque) dans un "
                "seul thread, en cédant la main à chaque await."
            ),
            points=[
                "Une fonction async def renvoie une coroutine : l'appeler ne l'exécute pas, "
                "il faut l'attendre avec await ou la lancer avec asyncio.run().",
                "C'est du multitâche coopératif : la boucle d'événements passe à une autre "
                "tâche quand la première attend, alors que les threads sont préemptés par "
                "l'OS.",
                "Utile pour les tâches liées aux entrées-sorties (appels HTTP, LLM) ; inutile "
                "pour du calcul CPU, qui bloquerait la boucle.",
                "Exemple à citer : FastAPI sert d'autres requêtes pendant qu'une route "
                "attend la réponse d'un LLM.",
            ],
            source_label=ASYNCIO,
            source_url=ASYNCIO_URL,
            diagram=flow(["Tâche A attend", "Boucle d'événements", "Tâche B s'exécute"]),
        ),
        CardContent(
            titre="Asyncio : lancer des tâches en parallèle",
            accroche=(
                "Un await dans une boucle exécute les tâches l'une après l'autre ; "
                "asyncio.gather() les lance ensemble et gagne du temps."
            ),
            points=[
                "Six appels d'une seconde attendus un par un coûtent 6 s ; lancés avec "
                "await asyncio.gather(*coros) ils coûtent environ 1 s.",
                "gather() renvoie les résultats dans l'ordre des coroutines données.",
                "Piège : une bibliothèque bloquante comme requests gèle la boucle ; il faut "
                "un client asynchrone (httpx.AsyncClient, aiohttp).",
                "asyncio.Queue n'est pas thread-safe : elle sert à échanger entre tâches "
                "de la même boucle, pas entre threads.",
            ],
            source_label=ASYNCIO,
            source_url=ASYNCIO_URL,
        ),
        CardContent(
            titre="Logging : loggers, niveaux et handlers",
            essentielle=True,
            accroche=(
                "Le module logging de la bibliothèque standard remplace print : il "
                "classe les messages par gravité et les envoie où l'on veut."
            ),
            points=[
                "Cinq niveaux, du moins au plus grave : DEBUG, INFO, WARNING, ERROR, "
                "CRITICAL ; on règle un seuil et tout ce qui est en dessous est ignoré.",
                "Un logger émet le message, un handler choisit la destination (console, "
                "fichier, syslog, HTTP), un formatter fixe le format.",
                "Convention : log = logging.getLogger(__name__) dans chaque module ; seule "
                "l'application configure les sorties.",
                "Exemple à citer : en conteneur, logger sur la sortie standard et laisser "
                "la plateforme collecter.",
            ],
            source_label=LOGGING,
            source_url=LOGGING_URL,
            diagram=flow(["Logger", "Handler", "Formatter", "Console ou fichier"]),
        ),
        CardContent(
            titre="Logging : bonnes pratiques",
            accroche=(
                "Quelques habitudes évitent les logs inutilisables : configurer tôt, tracer "
                "les exceptions, ne jamais logger de secrets."
            ),
            points=[
                "logging.basicConfig(level=...) tôt dans le programme, avec le niveau lu dans "
                "une variable d'environnement.",
                "Dans un except, logging.exception('contexte') enregistre le message avec la "
                "trace complète de l'erreur.",
                "Une trace multi-lignes gêne les outils d'analyse : un formatter sur une "
                "ligne règle le problème.",
                "Ne pas logger de clés, mots de passe ou données personnelles ; attention "
                "aux handlers bloquants (réseau) qui peuvent ralentir l'application.",
            ],
            source_label=LOGGING,
            source_url=LOGGING_URL,
        ),
        CardContent(
            titre="Python Fire : une ligne de commande depuis une fonction",
            accroche=(
                "Fire génère automatiquement une interface en ligne de commande à partir "
                "de n'importe quelle fonction, classe ou objet Python."
            ),
            points=[
                "Installation : pip install fire ; puis fire.Fire(ma_fonction) suffit.",
                "Les paramètres deviennent des options : python hello.py --name=David ; "
                "avec une classe, ses méthodes deviennent des sous-commandes.",
                "Utile pour explorer du code existant, déboguer ou transformer vite un "
                "script en outil ; l'option -- --help affiche l'aide générée.",
                "À réserver aux outils internes : pour une CLI publique et très soignée, "
                "on préfère argparse ou click.",
            ],
            source_label=FIRE,
            source_url=FIRE_URL,
        ),
        CardContent(
            titre="mypy : vérifier les types sans exécuter",
            essentielle=True,
            accroche=(
                "mypy lit le code et signale les incohérences de types avant l'exécution, "
                "comme un correcteur orthographique pour les types."
            ),
            points=[
                "Installation : python -m pip install mypy ; lancement : mypy programme.py.",
                "Exemple : def greeting(name: str) -> str appelée avec greeting(3) est "
                "signalée comme erreur, sans lancer le programme.",
                "Types usuels : list[str], int | str, Iterable[str] ; un isinstance() "
                "affine le type dans la branche concernée.",
                "Pour une bibliothèque sans types, on installe un paquet de stubs "
                "(types-requests, types-PyYAML).",
            ],
            source_label=MYPY,
            source_url=MYPY_URL,
        ),
        CardContent(
            titre="mypy : typage progressif et mode strict",
            accroche=(
                "Par défaut mypy ignore les fonctions sans annotations ; des options "
                "permettent d'imposer le typage de plus en plus tôt."
            ),
            points=[
                "--check-untyped-defs vérifie quand même le corps des fonctions non "
                "annotées ; --disallow-untyped-defs refuse les fonctions sans annotations.",
                "--strict active tout un ensemble de contrôles stricts ; c'est le réglage "
                "de ce projet.",
                "--ignore-missing-imports tait les bibliothèques sans types, à utiliser "
                "avec parcimonie.",
                "Sur un code existant, on adopte mypy progressivement, module par module.",
            ],
            source_label=MYPY,
            source_url=MYPY_URL,
        ),
        CardContent(
            titre="uv : gestionnaire de paquets et d'environnements",
            essentielle=True,
            accroche=(
                "uv, écrit en Rust, remplace à lui seul pip, virtualenv, pyenv et pip-tools, "
                "et il est très rapide."
            ),
            points=[
                "uv init crée un projet, uv add paquet l'ajoute dans pyproject.toml, "
                "uv remove le retire, uv run script.py exécute dans l'environnement du projet.",
                "uv.lock fige les versions exactes de toutes les dépendances : à committer "
                "pour que tout le monde installe la même chose.",
                "uv python install 3.12 installe une version de Python ; uvx ruff check . "
                "lance un outil dans un environnement temporaire.",
                "Ordre de grandeur annoncé par l'article : 10 à 100 fois plus rapide que pip.",
            ],
            source_label=UV,
            source_url=UV_URL,
            diagram=flow(["uv init", "uv add", "uv.lock", "uv run"]),
        ),
        CardContent(
            titre="uv : reproductibilité, CI et migration",
            accroche=(
                "uv rend les installations reproductibles et facilite le passage "
                "depuis requirements.txt et l'usage en CI ou en conteneur."
            ),
            points=[
                "uv sync installe exactement ce que dit uv.lock ; --frozen échoue en CI si "
                "le lock n'est pas à jour.",
                "Migration : uv pip install -r requirements.txt, et uv export -o "
                "requirements.txt pour repartir dans l'autre sens.",
                "Scripts autonomes : un bloc de commentaires « # /// script » (PEP 723) "
                "déclare les dépendances dans le fichier.",
                "Dans Docker, copier pyproject.toml et uv.lock avant le code profite du "
                "cache de couches.",
            ],
            source_label=UV,
            source_url=UV_URL,
        ),
    ],
)
