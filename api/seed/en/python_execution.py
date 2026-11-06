"""English version of the Python execution theme (same cards, same order as the French)."""

from api.course_models import CardTranslation, ThemeTranslation

ASYNCIO = "Asyncio (Built In)"
LOGGING = "Python logging basics (Loggly)"
FIRE = "Python Fire (Google, GitHub)"
MYPY = "mypy: Getting started (official documentation)"
UV = "Python UV (DataCamp)"

THEME = ThemeTranslation(
    slug="python-execution",
    titre="Python: execution and quality",
    source_label="Sources listed on each card",
    cards=[
        CardTranslation(
            titre="Asyncio: async and await",
            accroche=(
                "Asyncio handles many waits (network, database, disk) in a single thread, "
                "handing control back at every await."
            ),
            points=[
                "An async def function returns a coroutine: calling it does not run it, you "
                "must await it or start it with asyncio.run().",
                "It is cooperative multitasking: the event loop switches to another task when "
                "the first one waits, whereas threads are preempted by the OS.",
                "Useful for I/O-bound work (HTTP calls, LLMs); useless for CPU-heavy work, "
                "which would block the loop.",
                "Example to quote: FastAPI serves other requests while a route waits for an "
                "LLM response.",
            ],
            source_label=ASYNCIO,
            diagram_labels=["Task A waits", "Event loop", "Task B runs"],
        ),
        CardTranslation(
            titre="Asyncio: running tasks concurrently",
            accroche=(
                "An await inside a loop runs tasks one after the other; asyncio.gather() "
                "starts them together and saves time."
            ),
            points=[
                "Six one-second calls awaited one by one cost 6 s; started with "
                "await asyncio.gather(*coros) they cost about 1 s.",
                "gather() returns the results in the order of the coroutines given.",
                "Pitfall: a blocking library such as requests freezes the loop; use an async "
                "client (httpx.AsyncClient, aiohttp).",
                "asyncio.Queue is not thread-safe: it is for exchanging between tasks of the "
                "same loop, not between threads.",
            ],
            source_label=ASYNCIO,
        ),
        CardTranslation(
            titre="Logging: loggers, levels and handlers",
            accroche=(
                "The standard logging module replaces print: it ranks messages by severity "
                "and sends them wherever you want."
            ),
            points=[
                "Five levels, from least to most severe: DEBUG, INFO, WARNING, ERROR, "
                "CRITICAL; you set a threshold and anything below it is ignored.",
                "A logger emits the message, a handler picks the destination (console, file, "
                "syslog, HTTP), a formatter sets the format.",
                "Convention: log = logging.getLogger(__name__) in each module; only the "
                "application configures the outputs.",
                "Example to quote: in a container, log to standard output and let the "
                "platform collect it.",
            ],
            source_label=LOGGING,
            diagram_labels=["Logger", "Handler", "Formatter", "Console or file"],
        ),
        CardTranslation(
            titre="Logging: good practices",
            accroche=(
                "A few habits avoid unusable logs: configure early, trace exceptions, never "
                "log secrets."
            ),
            points=[
                "logging.basicConfig(level=...) early in the program, with the level read "
                "from an environment variable.",
                "Inside an except, logging.exception('context') records the message with the "
                "full error traceback.",
                "A multi-line traceback bothers analysis tools: a one-line formatter fixes "
                "that.",
                "Do not log keys, passwords or personal data; beware of blocking handlers "
                "(network) that can slow the application down.",
            ],
            source_label=LOGGING,
        ),
        CardTranslation(
            titre="Python Fire: a command line from a function",
            accroche=(
                "Fire automatically generates a command-line interface from any Python "
                "function, class or object."
            ),
            points=[
                "Install with pip install fire; then fire.Fire(my_function) is enough.",
                "Parameters become options: python hello.py --name=David; with a class, its "
                "methods become subcommands.",
                "Handy to explore existing code, debug, or quickly turn a script into a "
                "tool; -- --help shows the generated help.",
                "Keep it for internal tools: for a public, polished CLI, prefer argparse or "
                "click.",
            ],
            source_label=FIRE,
        ),
        CardTranslation(
            titre="mypy: checking types without running",
            accroche=(
                "mypy reads the code and reports type inconsistencies before execution, like "
                "a spell checker for types."
            ),
            points=[
                "Install with python -m pip install mypy; run with mypy program.py.",
                "Example: def greeting(name: str) -> str called as greeting(3) is flagged as "
                "an error, without running the program.",
                "Common types: list[str], int | str, Iterable[str]; an isinstance() narrows "
                "the type in the relevant branch.",
                "For a library without types, install a stubs package (types-requests, "
                "types-PyYAML).",
            ],
            source_label=MYPY,
        ),
        CardTranslation(
            titre="mypy: gradual typing and strict mode",
            accroche=(
                "By default mypy skips functions with no annotations; options let you "
                "require typing more and more."
            ),
            points=[
                "--check-untyped-defs still checks the body of unannotated functions; "
                "--disallow-untyped-defs rejects functions without annotations.",
                "--strict enables a whole set of strict checks; it is this project's "
                "setting.",
                "--ignore-missing-imports silences libraries without types, to be used "
                "sparingly.",
                "On existing code, adopt mypy gradually, module by module.",
            ],
            source_label=MYPY,
        ),
        CardTranslation(
            titre="uv: package and environment manager",
            accroche=(
                "uv, written in Rust, replaces pip, virtualenv, pyenv and pip-tools on its "
                "own, and it is very fast."
            ),
            points=[
                "uv init creates a project, uv add package adds it to pyproject.toml, "
                "uv remove drops it, uv run script.py runs in the project's environment.",
                "uv.lock pins the exact versions of every dependency: commit it so everyone "
                "installs the same thing.",
                "uv python install 3.12 installs a Python version; uvx ruff check . runs a "
                "tool in a temporary environment.",
                "Order of magnitude claimed by the article: 10 to 100 times faster than pip.",
            ],
            source_label=UV,
            diagram_labels=["uv init", "uv add", "uv.lock", "uv run"],
        ),
        CardTranslation(
            titre="uv: reproducibility, CI and migration",
            accroche=(
                "uv makes installs reproducible and eases the move from requirements.txt and "
                "use in CI or containers."
            ),
            points=[
                "uv sync installs exactly what uv.lock says; --frozen fails in CI if the "
                "lock is out of date.",
                "Migration: uv pip install -r requirements.txt, and uv export -o "
                "requirements.txt to go back the other way.",
                "Standalone scripts: a '# /// script' comment block (PEP 723) declares the "
                "dependencies inside the file.",
                "In Docker, copying pyproject.toml and uv.lock before the code takes "
                "advantage of layer caching.",
            ],
            source_label=UV,
        ),
    ],
)
