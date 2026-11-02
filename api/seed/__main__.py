"""Point d'entrée : migre la base puis insère le contenu du cours."""

from api.db import connect, migrate
from api.deps import settings
from api.seed.runner import THEMES, seed_all


def main() -> None:
    """Applique les migrations puis le seed."""
    conn = connect(settings.db_path)
    migrate(conn)
    seed_all(conn)
    conn.close()
    cards = sum(len(theme.cards) for theme in THEMES)
    print(f"Seed terminé : {len(THEMES)} thème(s), {cards} carte(s).")


if __name__ == "__main__":
    main()
