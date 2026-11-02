"""Accès SQL au System Design : cas, sessions, chat, versions de scène."""

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import JsonValue

from api.sd_correction_models import ReferenceSolution, SdCorrection
from api.sd_models import (
    CaseOut,
    GeneratedCase,
    HiddenContext,
    SceneOut,
    SceneVersion,
    SdMessage,
    SdSessionSummary,
    SdStatut,
)

MAX_SCENE_VERSIONS = 100

CASE_SELECT = (
    "SELECT c.id, c.type, c.titre, c.brief, "
    "(SELECT COUNT(*) FROM sd_sessions s WHERE s.case_id = c.id) AS nb_sessions "
    "FROM sd_cases c "
)


@dataclass(frozen=True)
class SessionRow:
    """État brut d'une session."""

    id: int
    created_at: str
    statut: SdStatut
    elapsed_s: int
    case_id: int
    summary: str
    summary_upto: int


def _now() -> str:
    """Horodatage UTC ISO."""
    return datetime.now(UTC).isoformat()


def _to_case(row: sqlite3.Row) -> CaseOut:
    """Convertit une ligne SQL en cas d'API (sans détails cachés)."""
    return CaseOut(
        id=row["id"],
        type=row["type"],
        titre=row["titre"],
        brief=row["brief"],
        nb_sessions=row["nb_sessions"],
    )


# --- Cas ---


def insert_case(conn: sqlite3.Connection, type_slug: str, generated: GeneratedCase) -> CaseOut:
    """Range un cas généré dans la banque ; les détails cachés restent en base."""
    hidden = HiddenContext(details=generated.details, pistes_zoom=generated.pistes_zoom)
    cursor = conn.execute(
        "INSERT INTO sd_cases (type, titre, brief, params_json, created_at) VALUES (?, ?, ?, ?, ?)",
        (type_slug, generated.titre, generated.brief, hidden.model_dump_json(), _now()),
    )
    conn.commit()
    case = get_case(conn, int(cursor.lastrowid or 0))
    if case is None:
        raise RuntimeError("cas introuvable après insertion")
    return case


def get_case(conn: sqlite3.Connection, case_id: int) -> CaseOut | None:
    """Retourne un cas par identifiant."""
    row = conn.execute(CASE_SELECT + "WHERE c.id = ?", (case_id,)).fetchone()
    return _to_case(row) if row else None


def get_hidden(conn: sqlite3.Connection, case_id: int) -> HiddenContext:
    """Détails cachés d'un cas (usage interne : prompt de l'interviewer)."""
    row = conn.execute("SELECT params_json FROM sd_cases WHERE id = ?", (case_id,)).fetchone()
    return HiddenContext.model_validate_json(row["params_json"])


def list_cases(conn: sqlite3.Connection, type_slug: str | None) -> list[CaseOut]:
    """Liste la banque de cas, du plus récent au plus ancien."""
    where, params = ("WHERE c.type = ? ", [type_slug]) if type_slug else ("", [])
    rows = conn.execute(CASE_SELECT + where + "ORDER BY c.id DESC", params).fetchall()
    return [_to_case(row) for row in rows]


def draw_case(conn: sqlite3.Connection, type_slug: str | None) -> CaseOut | None:
    """Tire un cas de la banque en favorisant les moins joués."""
    where, params = ("WHERE c.type = ? ", [type_slug]) if type_slug else ("", [])
    row = conn.execute(
        CASE_SELECT + where + "ORDER BY nb_sessions ASC, RANDOM() LIMIT 1", params
    ).fetchone()
    return _to_case(row) if row else None


# --- Sessions et chat ---


def create_session(conn: sqlite3.Connection, case_id: int, opening: str) -> int:
    """Crée une session dont le premier message (interviewer) est l'énoncé du cas."""
    now = _now()
    cursor = conn.execute(
        "INSERT INTO sd_sessions (case_id, created_at) VALUES (?, ?)", (case_id, now)
    )
    session_id = int(cursor.lastrowid or 0)
    conn.execute(
        "INSERT INTO sd_messages (session_id, role, content, created_at) "
        "VALUES (?, 'assistant', ?, ?)",
        (session_id, opening, now),
    )
    conn.commit()
    return session_id


def get_session_row(conn: sqlite3.Connection, session_id: int) -> SessionRow | None:
    """Retourne l'état brut d'une session."""
    row = conn.execute(
        "SELECT id, created_at, statut, elapsed_s, case_id, summary, summary_upto "
        "FROM sd_sessions WHERE id = ?",
        (session_id,),
    ).fetchone()
    return SessionRow(**dict(row)) if row else None


def list_messages(conn: sqlite3.Connection, session_id: int) -> list[SdMessage]:
    """Messages du chat dans l'ordre."""
    rows = conn.execute(
        "SELECT id, role, content, created_at FROM sd_messages WHERE session_id = ? ORDER BY id",
        (session_id,),
    ).fetchall()
    return [SdMessage(**dict(row)) for row in rows]


def add_message(conn: sqlite3.Connection, session_id: int, role: str, content: str) -> None:
    """Ajoute un message au chat."""
    conn.execute(
        "INSERT INTO sd_messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, content, _now()),
    )
    conn.commit()


def set_elapsed(conn: sqlite3.Connection, session_id: int, elapsed_s: int) -> None:
    """Enregistre le temps passé (jamais en arrière)."""
    conn.execute(
        "UPDATE sd_sessions SET elapsed_s = MAX(elapsed_s, ?) WHERE id = ?", (elapsed_s, session_id)
    )
    conn.commit()


def set_summary(conn: sqlite3.Connection, session_id: int, summary: str, upto: int) -> None:
    """Enregistre le résumé glissant et le dernier message résumé."""
    conn.execute(
        "UPDATE sd_sessions SET summary = ?, summary_upto = ? WHERE id = ?",
        (summary, upto, session_id),
    )
    conn.commit()


def finish_session(conn: sqlite3.Connection, session_id: int) -> None:
    """Marque la session comme terminée (sans effet si elle l'est déjà)."""
    conn.execute(
        "UPDATE sd_sessions SET statut = 'terminee', ended_at = COALESCE(ended_at, ?) WHERE id = ?",
        (_now(), session_id),
    )
    conn.commit()


def list_session_summaries(conn: sqlite3.Connection) -> list[SdSessionSummary]:
    """Sessions, de la plus récente à la plus ancienne."""
    rows = conn.execute(
        "SELECT s.id, s.created_at, s.statut, s.elapsed_s, c.type, c.titre, "
        "(SELECT COUNT(*) FROM sd_messages m WHERE m.session_id = s.id) AS nb_messages "
        "FROM sd_sessions s JOIN sd_cases c ON c.id = s.case_id ORDER BY s.id DESC"
    ).fetchall()
    return [SdSessionSummary(**dict(row)) for row in rows]


# --- Versions de scène ---


def scene_hash(elements: list[dict[str, JsonValue]], app_state: dict[str, JsonValue]) -> str:
    """Empreinte stable d'une scène, pour ne pas enregistrer deux fois la même."""
    payload = json.dumps({"e": elements, "a": app_state}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def save_scene(
    conn: sqlite3.Connection,
    session_id: int,
    elements: list[dict[str, JsonValue]],
    app_state: dict[str, JsonValue],
) -> SceneVersion:
    """Enregistre une nouvelle version si la scène a changé ; élague les plus anciennes."""
    digest = scene_hash(elements, app_state)
    latest = conn.execute(
        "SELECT version, created_at, content_hash FROM sd_scenes WHERE session_id = ? "
        "ORDER BY version DESC LIMIT 1",
        (session_id,),
    ).fetchone()
    if latest and latest["content_hash"] == digest:
        return SceneVersion(version=latest["version"], created_at=latest["created_at"])
    version = (latest["version"] if latest else 0) + 1
    created_at = _now()
    scene_json = json.dumps({"elements": elements, "app_state": app_state}, ensure_ascii=False)
    conn.execute(
        "INSERT INTO sd_scenes (session_id, version, scene_json, created_at, content_hash) "
        "VALUES (?, ?, ?, ?, ?)",
        (session_id, version, scene_json, created_at, digest),
    )
    conn.execute(
        "DELETE FROM sd_scenes WHERE session_id = ? AND version <= ?",
        (session_id, version - MAX_SCENE_VERSIONS),
    )
    conn.commit()
    return SceneVersion(version=version, created_at=created_at)


def get_scene(conn: sqlite3.Connection, session_id: int, version: int | None) -> SceneOut | None:
    """Retourne une version précise de la scène, ou la dernière si `version` est None."""
    if version is None:
        row = conn.execute(
            "SELECT version, created_at, scene_json FROM sd_scenes WHERE session_id = ? "
            "ORDER BY version DESC LIMIT 1",
            (session_id,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT version, created_at, scene_json FROM sd_scenes "
            "WHERE session_id = ? AND version = ?",
            (session_id, version),
        ).fetchone()
    if row is None:
        return None
    data = json.loads(row["scene_json"])
    return SceneOut(
        version=row["version"],
        created_at=row["created_at"],
        elements=data["elements"],
        app_state=data["app_state"],
    )


def list_scene_versions(conn: sqlite3.Connection, session_id: int) -> list[SceneVersion]:
    """Versions de scène, de la plus récente à la plus ancienne."""
    rows = conn.execute(
        "SELECT version, created_at FROM sd_scenes WHERE session_id = ? ORDER BY version DESC",
        (session_id,),
    ).fetchall()
    return [SceneVersion(**dict(row)) for row in rows]


# --- Solution de référence (par cas) et correction (par session) ---


def get_reference(conn: sqlite3.Connection, case_id: int) -> ReferenceSolution | None:
    """Solution de référence déjà générée pour ce cas, s'il y en a une."""
    row = conn.execute("SELECT contenu FROM sd_references WHERE case_id = ?", (case_id,)).fetchone()
    return ReferenceSolution.model_validate_json(row["contenu"]) if row else None


def save_reference(conn: sqlite3.Connection, case_id: int, reference: ReferenceSolution) -> None:
    """Met la solution de référence en cache pour ce cas."""
    conn.execute(
        "INSERT INTO sd_references (case_id, contenu, created_at) VALUES (?, ?, ?) "
        "ON CONFLICT(case_id) DO UPDATE SET contenu = excluded.contenu, "
        "created_at = excluded.created_at",
        (case_id, reference.model_dump_json(), _now()),
    )
    conn.commit()


def get_correction(conn: sqlite3.Connection, session_id: int) -> SdCorrection | None:
    """Correction déjà générée pour cette session, s'il y en a une."""
    row = conn.execute(
        "SELECT correction_json FROM sd_corrections WHERE session_id = ?", (session_id,)
    ).fetchone()
    return SdCorrection.model_validate_json(row["correction_json"]) if row else None


def save_correction(conn: sqlite3.Connection, session_id: int, correction: SdCorrection) -> None:
    """Enregistre la correction de la session."""
    conn.execute(
        "INSERT INTO sd_corrections (session_id, correction_json, created_at) VALUES (?, ?, ?) "
        "ON CONFLICT(session_id) DO UPDATE SET correction_json = excluded.correction_json, "
        "created_at = excluded.created_at",
        (session_id, correction.model_dump_json(), _now()),
    )
    conn.commit()
