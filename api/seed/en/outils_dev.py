"""English version of the everyday tools theme (same cards, same order as the French)."""

from api.course_models import CardTranslation, ThemeTranslation

GIT = "Git Crash Course for Beginners (brandon1024, GitHub Gist)"
PRECOMMIT = "pre-commit documentation"
IDE = "PyCharm vs VSCode (Tangent Technologies, 2020)"
POSTMAN = "How to Use an API with Postman (freeCodeCamp, 2023)"

THEME = ThemeTranslation(
    slug="outils-dev",
    titre="Everyday tools",
    source_label="Sources listed on each card",
    cards=[
        CardTranslation(
            titre="Git: the four zones of a repository",
            accroche=(
                "Git moves code between four zones: the working directory, the index, the "
                "local repository and the remote repository."
            ),
            points=[
                "Workspace: your files being edited. git add puts them in the index "
                "(staging), the list of what will be committed.",
                "git commit records the index in the local repository; git push sends it to "
                "the remote; git pull (fetch plus integration) brings it back.",
                "git status before git add . avoids including files by mistake; "
                "git log --oneline --graph shows the history.",
                "Starting configuration: git config --global user.name and user.email.",
            ],
            source_label=GIT,
            diagram_labels=["Workspace", "Index", "Local repository", "Remote repository"],
        ),
        CardTranslation(
            titre="Git: branches, merge and rebase",
            accroche=(
                "You work on one branch per feature, then bring it into the main branch "
                "with a merge or a rebase."
            ),
            points=[
                "git checkout -b my-feature creates and switches to a branch; git branch "
                "lists them, -d deletes an already merged branch.",
                "Merge creates a merge commit and keeps history as is; rebase replays your "
                "commits on top of the target branch for a linear history.",
                "Golden rule of rebase: do not rewrite commits already shared; the choice "
                "depends on the team's practices.",
                "Git-Flow is a branching convention (master, staging, develop and feature "
                "branches).",
            ],
            source_label=GIT,
        ),
        CardTranslation(
            titre="Git: setting aside and undoing",
            accroche=(
                "stash sets work aside, reset goes back in history: useful, but reset --hard "
                "is destructive."
            ),
            points=[
                "git stash tucks away current changes; git stash pop brings them back, handy "
                "to switch branch in a hurry.",
                "git reset --soft HEAD^ undoes the last commit keeping the changes staged; "
                "--mixed (the default) keeps them unstaged.",
                "git reset --hard also erases changes in the working directory: irreversible.",
                "Avoid git push -f on a shared branch, unless you know exactly what you are "
                "rewriting.",
            ],
            source_label=GIT,
        ),
        CardTranslation(
            titre="Pre-commit: checks before every commit",
            accroche=(
                "pre-commit automatically runs checks (formatting, lint, types) on the "
                "changed files before accepting a commit."
            ),
            points=[
                "A Git pre-commit hook runs on git commit; if a check fails, the commit is "
                "refused.",
                "Benefit: silly mistakes (whitespace, unused imports, secrets) are stopped "
                "before CI and before code review.",
                "The pre-commit framework manages hooks for the whole team, from a single "
                "versioned file.",
                "Many hooks fix things themselves (formatting): review the diff, then rerun "
                "the commit.",
            ],
            source_label=PRECOMMIT,
            diagram_labels=["git commit", "pre-commit hooks", "Commit accepted or refused"],
        ),
        CardTranslation(
            titre="Pre-commit: configuring and installing",
            accroche=(
                "You describe the checks in .pre-commit-config.yaml, install the hooks once, "
                "and everyone benefits."
            ),
            points=[
                "The .pre-commit-config.yaml file lists hook repositories, with a pinned "
                "version (rev) and the ids of the hooks wanted.",
                "pre-commit install wires the hooks into the local repository; everyone "
                "must do it once after a clone.",
                "pre-commit run --all-files runs everything on the whole codebase, useful "
                "when adding a new check or in CI.",
                "Example to quote: ruff and mypy as hooks, so the repository stays clean "
                "without thinking about it.",
            ],
            source_label=PRECOMMIT,
        ),
        CardTranslation(
            titre="PyCharm or VS Code?",
            accroche=(
                "PyCharm is a full-featured Python-specific IDE; VS Code is a light, "
                "versatile editor extended by plugins."
            ),
            points=[
                "PyCharm wins on refactoring, completion, debugging and Git integration; the "
                "cited study gives 33/35 against 23/35 for VS Code.",
                "VS Code starts faster (about 4 s against 15 s) but, in that test, used more "
                "memory (about 895 MB against 550 MB).",
                "VS Code remains the Swiss Army knife for several languages; PyCharm is the "
                "obvious choice if you mostly write Python.",
                "Caveat: the article dates from 2020 and tests a very simple project; both "
                "tools have evolved a lot since.",
            ],
            source_label=IDE,
        ),
        CardTranslation(
            titre="Postman: testing an API by hand",
            accroche=(
                "Postman is a graphical client to send HTTP requests to an API and inspect "
                "its responses without writing code."
            ),
            points=[
                "Methods: GET reads, POST creates (JSON body), PUT updates, DELETE removes.",
                "You set the URL, the query parameters (?category=books), the headers and "
                "the body (Body tab, in JSON format).",
                "Authentication: an API key in a header (X-API-Key) or a Bearer token in "
                "Authorization: Bearer <token>.",
                "Example to quote: call GET /health on a FastAPI API to check that it "
                "responds.",
            ],
            source_label=POSTMAN,
        ),
        CardTranslation(
            titre="Postman: collections and tests",
            accroche=(
                "You organize requests into collections, add automatic tests and share it "
                "all with the team."
            ),
            points=[
                "A collection groups related requests; it can be exported, imported and "
                "shared.",
                "The Tests tab accepts JavaScript: pm.test('OK', () => "
                "pm.response.to.have.status(200)).",
                "Pre-request scripts prepare the request (add a header, compute a value) "
                "before it is sent.",
                "On failure, check in order: connection, endpoint URL, credentials, request "
                "structure.",
            ],
            source_label=POSTMAN,
        ),
    ],
)
