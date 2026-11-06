"""English version of the Python data theme (same cards, same order as the French)."""

from api.course_models import CardTranslation, ThemeTranslation

PYDANTIC = "Pydantic documentation"
SQLALCHEMY = "SQLAlchemy 2.0 documentation"
SQLMODEL = "SQLModel ORM (Better Stack, 2025)"
ALEMBIC = "Simplify database migrations with Alembic (dev.to, 2024)"

THEME = ThemeTranslation(
    slug="python-donnees",
    titre="Python: data and databases",
    source_label="Sources listed on each card",
    cards=[
        CardTranslation(
            titre="Pydantic: validating data with types",
            accroche=(
                "Pydantic turns Python type annotations into validation: you describe the "
                "expected shape of the data, and anything that does not fit is rejected."
            ),
            points=[
                "You write a class inheriting from BaseModel with typed fields; on creation, "
                "Pydantic checks and converts each value ('3' becomes 3).",
                "If data is invalid it raises a ValidationError listing every faulty field "
                "and why, instead of an obscure error later on.",
                "model_dump() and model_dump_json() serialize the model; model_validate() "
                "builds a model from a dict.",
                "Typical use: validate at the boundary (FastAPI request body, LLM output, "
                "config file) so the rest of the code handles safe data.",
            ],
            source_label=PYDANTIC,
            diagram_labels=["Raw data", "Pydantic model", "Valid object or error"],
        ),
        CardTranslation(
            titre="Pydantic: constraints and validators",
            accroche=(
                "Beyond the type, Pydantic expresses business rules: bounds, lengths, "
                "default values and custom validators."
            ),
            points=[
                "Field(ge=0, le=100, max_length=40, default=...) sets bounds and defaults "
                "directly on the field.",
                "@field_validator checks or cleans one field; @model_validator enforces a "
                "rule across several fields (e.g. start before end).",
                "An Optional[str] = None field is optional; a field with no default is "
                "required.",
                "By default Pydantic converts values (lax mode); in strict mode, '3' for an "
                "integer is rejected.",
            ],
            source_label=PYDANTIC,
        ),
        CardTranslation(
            titre="SQLAlchemy: Core and ORM",
            accroche=(
                "SQLAlchemy is the reference SQL toolkit in Python, with two levels: Core to "
                "build SQL, ORM to work with objects."
            ),
            points=[
                "Core: you compose SQL queries in Python (select, insert...) and run them "
                "through a connection; close to SQL, very controllable.",
                "ORM: you declare classes (User, Order) mapped to tables, and read or write "
                "objects instead of rows.",
                "In SQLAlchemy 2.0 you declare with DeclarativeBase, Mapped[int] and "
                "mapped_column(), which works well with mypy.",
                "The same code runs on SQLite, PostgreSQL, MySQL: only the connection URL "
                "changes.",
            ],
            source_label=SQLALCHEMY,
        ),
        CardTranslation(
            titre="SQLAlchemy: engine, session and transaction",
            accroche=(
                "The engine manages the database connection, the session groups changes into "
                "one transaction committed in one go."
            ),
            points=[
                "create_engine('sqlite:///app.db') creates the engine, built once and "
                "shared; it manages a connection pool.",
                "A Session tracks loaded or added objects; session.add() stages, "
                "session.commit() writes everything in one transaction, rollback() cancels.",
                "You read with session.scalars(select(User).where(User.age > 18)).all().",
                "Classic pitfall: lazy loading of relationships runs one query per object "
                "(the N+1 problem); selectinload() loads them in one go.",
            ],
            source_label=SQLALCHEMY,
        ),
        CardTranslation(
            titre="SQLModel: one class for the table and the validation",
            accroche=(
                "SQLModel combines SQLAlchemy and Pydantic: one class describes the database "
                "table and validates the API data."
            ),
            points=[
                "You declare a typed class; with table=True it becomes a table "
                "(Optional[int] = Field(default=None, primary_key=True) for the id).",
                "Without table=True, the class is a pure Pydantic model, handy for API "
                "input and output schemas (create, read).",
                "It is written by the author of FastAPI so the two fit together without "
                "duplication.",
                "Watch out: a table=True model does not validate on construction; validation "
                "goes through a model without a table.",
            ],
            source_label=SQLMODEL,
            diagram_labels=["SQLModel class", "SQL table", "Validated API schema"],
        ),
        CardTranslation(
            titre="SQLModel: queries with select and Session",
            accroche=(
                "With SQLModel you create the engine, open a session and query with "
                "select(); the result is directly a typed object."
            ),
            points=[
                "SQLModel.metadata.create_all(engine) creates the tables that do not exist; "
                "in production, prefer migrations.",
                "Read: session.exec(select(Book).where(Book.pages > 300)).all().",
                "Write: session.add(obj) does nothing in the database until you call "
                "session.commit().",
                "Good practice: with Session(engine) as session: closes the session "
                "cleanly even on error.",
            ],
            source_label=SQLMODEL,
        ),
        CardTranslation(
            titre="Alembic: why migrations",
            accroche=(
                "A migration is a versioned change to the database schema; Alembic writes, "
                "applies and reverts them reproducibly."
            ),
            points=[
                "Without migrations, each environment (dev, test, prod) ends up with a "
                "slightly different schema; with them, everyone follows the same history.",
                "Alembic builds on SQLAlchemy; each migration is a Python script with an "
                "upgrade() function and a downgrade() function.",
                "Migrations are versioned in Git with the code and replayable in CI/CD.",
                "An alembic_version table remembers the revision currently applied.",
            ],
            source_label=ALEMBIC,
            diagram_labels=["Revision 1", "Revision 2", "Revision 3 (head)"],
        ),
        CardTranslation(
            titre="Alembic: writing and applying a migration",
            accroche=(
                "You generate a migration script, complete it, then move up or down one "
                "version with a few commands."
            ),
            points=[
                "alembic init creates the config; alembic revision -m 'message' creates a "
                "script (--autogenerate infers it from the SQLAlchemy models).",
                "Always review the generated script: autogenerate misses some cases (a "
                "rename becomes a drop plus an add).",
                "alembic upgrade head applies everything; alembic downgrade -1 reverts the "
                "last one; alembic current and alembic history show the state.",
                "Watch out: a downgrade can destroy data (e.g. DROP ... CASCADE); do not put "
                "database credentials in plain text in alembic.ini.",
            ],
            source_label=ALEMBIC,
        ),
    ],
)
