"""Point d'entrée : migre la base puis insère le contenu du cours."""

from api.db import connect, migrate
from api.deps import settings
from api.seed.runner import THEMES, seed_all
from api.seed.workflows import THEMES as WF_THEMES
from api.seed.workflows.runner import seed_workflows


def main() -> None:
    """Applique les migrations puis le seed."""
    conn = connect(settings.db_path)
    migrate(conn)
    seed_all(conn)
    seed_workflows(conn)
    conn.close()
    cards = sum(len(theme.cards) for theme in THEMES)
    print(f"Seed terminé : {len(THEMES)} thème(s), {cards} carte(s).")
    wf_cards = sum(len(theme.cards) for theme in WF_THEMES)
    print(f"Mistral Workflows : {len(WF_THEMES)} catégorie(s), {wf_cards} carte(s).")


if __name__ == "__main__":
    main()
