"""Contenu du thème Python : données et base de données (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow

PYDANTIC = "Documentation Pydantic"
PYDANTIC_URL = "https://docs.pydantic.dev/latest/"
SQLALCHEMY = "Documentation SQLAlchemy 2.0"
SQLALCHEMY_URL = "https://docs.sqlalchemy.org/en/20/tutorial/"
SQLMODEL = "SQLModel ORM (Better Stack, 2025)"
SQLMODEL_URL = "https://betterstack.com/community/guides/scaling-python/sqlmodel-orm/"
ALEMBIC = "Simplify database migrations with Alembic (dev.to, 2024)"
ALEMBIC_URL = "https://dev.to/r0mymendez/simplify-database-migrations-using-python-with-alembic-4bhd"

THEME = ThemeContent(
    slug="python-donnees",
    titre="Python : données et base de données",
    source_label="Sources indiquées sur chaque carte",
    source_url=None,
    cards=[
        CardContent(
            titre="Pydantic : valider des données avec des types",
            essentielle=True,
            accroche=(
                "Pydantic transforme des annotations de type Python en validation : on décrit la "
                "forme attendue des données, et tout ce qui ne colle pas est refusé."
            ),
            points=[
                "On écrit une classe qui hérite de BaseModel avec des champs typés ; à la "
                "création, Pydantic vérifie et convertit chaque valeur (« 3 » devient 3).",
                "Si une donnée est invalide, il lève une ValidationError qui liste chaque "
                "champ fautif et la raison, au lieu d'une erreur obscure plus tard.",
                "model_dump() et model_dump_json() sérialisent le modèle ; model_validate() "
                "construit un modèle à partir d'un dict.",
                "Usage type : valider à la frontière (corps d'une requête FastAPI, sortie d'un "
                "LLM, fichier de config) pour que le reste du code manipule des données sûres.",
            ],
            source_label=PYDANTIC,
            source_url=PYDANTIC_URL,
            diagram=flow(["Données brutes", "Modèle Pydantic", "Objet valide ou erreur"]),
        ),
        CardContent(
            titre="Pydantic : contraintes et validateurs",
            accroche=(
                "Au-delà du type, Pydantic permet d'exprimer des règles métier : bornes, "
                "longueurs, valeurs par défaut et validateurs personnalisés."
            ),
            points=[
                "Field(ge=0, le=100, max_length=40, default=...) pose des bornes et des "
                "défauts directement sur le champ.",
                "@field_validator contrôle ou nettoie un champ ; @model_validator vérifie une "
                "règle qui porte sur plusieurs champs (ex. début avant fin).",
                "Un champ Optional[str] = None est facultatif ; un champ sans valeur par défaut "
                "est obligatoire.",
                "Par défaut Pydantic convertit (mode souple) ; en mode strict, « 3 » pour un "
                "entier est refusé.",
            ],
            source_label=PYDANTIC,
            source_url=PYDANTIC_URL,
        ),
        CardContent(
            titre="SQLAlchemy : Core et ORM",
            essentielle=True,
            accroche=(
                "SQLAlchemy est la boîte à outils SQL de référence en Python, avec deux "
                "niveaux : Core pour construire du SQL, ORM pour manipuler des objets."
            ),
            points=[
                "Core : on compose des requêtes SQL en Python (select, insert...) et on les "
                "exécute via une connexion ; proche du SQL, très contrôlable.",
                "ORM : on déclare des classes (User, Order) liées à des tables, et on lit ou "
                "écrit des objets plutôt que des lignes.",
                "En SQLAlchemy 2.0, on déclare avec DeclarativeBase, Mapped[int] et "
                "mapped_column(), ce qui s'accorde bien avec mypy.",
                "Le même code marche sur SQLite, PostgreSQL, MySQL : seule l'URL de connexion "
                "change.",
            ],
            source_label=SQLALCHEMY,
            source_url=SQLALCHEMY_URL,
        ),
        CardContent(
            titre="SQLAlchemy : engine, session et transaction",
            accroche=(
                "L'engine gère la connexion à la base, la session regroupe les changements en "
                "une transaction validée d'un seul coup."
            ),
            points=[
                "create_engine('sqlite:///app.db') crée l'engine, créé une seule fois et "
                "partagé ; il gère un pool de connexions.",
                "Une Session suit les objets chargés ou ajoutés ; session.add() prépare, "
                "session.commit() écrit tout dans une transaction, rollback() annule.",
                "On lit avec session.scalars(select(User).where(User.age > 18)).all().",
                "Piège classique : le chargement paresseux des relations lance une requête par "
                "objet (problème N+1) ; selectinload() les charge en une fois.",
            ],
            source_label=SQLALCHEMY,
            source_url=SQLALCHEMY_URL,
        ),
        CardContent(
            titre="SQLModel : une classe pour la table et la validation",
            essentielle=True,
            accroche=(
                "SQLModel combine SQLAlchemy et Pydantic : une même classe décrit la table en "
                "base et valide les données de l'API."
            ),
            points=[
                "On déclare une classe typée ; avec table=True elle devient une table "
                "(Optional[int] = Field(default=None, primary_key=True) pour l'identifiant).",
                "Sans table=True, la classe est un pur modèle Pydantic, pratique pour les "
                "schémas d'entrée et de sortie d'une API (création, lecture).",
                "Il est écrit par l'auteur de FastAPI pour que les deux s'emboîtent sans "
                "duplication.",
                "Attention : un modèle table=True ne valide pas à la construction ; la "
                "validation se fait via un modèle sans table.",
            ],
            source_label=SQLMODEL,
            source_url=SQLMODEL_URL,
            diagram=flow(["Classe SQLModel", "Table SQL", "Schéma API validé"]),
        ),
        CardContent(
            titre="SQLModel : requêtes avec select et Session",
            accroche=(
                "Avec SQLModel, on crée l'engine, on ouvre une session et on interroge avec "
                "select() ; le résultat est directement un objet typé."
            ),
            points=[
                "SQLModel.metadata.create_all(engine) crée les tables qui n'existent pas ; "
                "en production on préfère des migrations.",
                "Lecture : session.exec(select(Book).where(Book.pages > 300)).all().",
                "Écriture : session.add(obj) ne fait rien en base tant qu'on n'appelle pas "
                "session.commit().",
                "Bonne pratique : with Session(engine) as session: ferme la session "
                "proprement même en cas d'erreur.",
            ],
            source_label=SQLMODEL,
            source_url=SQLMODEL_URL,
        ),
        CardContent(
            titre="Alembic : pourquoi des migrations",
            essentielle=True,
            accroche=(
                "Une migration est une modification versionnée du schéma de la base ; Alembic "
                "les écrit, les applique et les annule de façon reproductible."
            ),
            points=[
                "Sans migrations, chaque environnement (dev, test, prod) finit avec un schéma "
                "légèrement différent ; avec elles, tout le monde suit le même historique.",
                "Alembic s'appuie sur SQLAlchemy ; chaque migration est un script Python avec "
                "une fonction upgrade() et une fonction downgrade().",
                "Les migrations sont versionnées dans Git avec le code et rejouables en CI/CD.",
                "Une table alembic_version retient la révision actuellement appliquée.",
            ],
            source_label=ALEMBIC,
            source_url=ALEMBIC_URL,
            diagram=flow(["Révision 1", "Révision 2", "Révision 3 (head)"]),
        ),
        CardContent(
            titre="Alembic : écrire et appliquer une migration",
            accroche=(
                "On génère un script de migration, on le complète, puis on monte ou on "
                "redescend d'une version avec quelques commandes."
            ),
            points=[
                "alembic init crée la config ; alembic revision -m 'message' crée un script "
                "(--autogenerate le déduit des modèles SQLAlchemy).",
                "Relire toujours le script généré : l'autogénération rate certains cas (un "
                "renommage devient suppression plus ajout).",
                "alembic upgrade head applique tout ; alembic downgrade -1 annule la dernière ; "
                "alembic current et alembic history montrent l'état.",
                "Attention : un downgrade peut détruire des données (ex. DROP ... CASCADE) ; "
                "ne pas mettre les identifiants de base en clair dans alembic.ini.",
            ],
            source_label=ALEMBIC,
            source_url=ALEMBIC_URL,
        ),
    ],
)
