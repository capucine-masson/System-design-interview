"""Accès SQL à l'entretien manager : banque de questions, sessions, réponses, retours."""

import json
import sqlite3
from datetime import UTC, datetime

from api.manager_models import (
    MAX_ANSWERS,
    Categorie,
    Difficulte,
    Feedback,
    GeneratedQuestion,
    Notes,
    QuestionOut,
    SessionOut,
    SessionSummary,
    Turn,
)

QUESTION_SELECT = (
    "SELECT q.id, q.categorie, q.difficulte, q.contexte, q.contraintes_json, q.enjeu, q.enonce, "
    "(SELECT COUNT(*) FROM manager_sessions s WHERE s.question_id = q.id) AS nb_sessions "
    "FROM manager_questions q "
)


def _now() -> str:
    """Horodatage UTC ISO."""
    return datetime.now(UTC).isoformat()


def _to_question(row: sqlite3.Row) -> QuestionOut:
    """Convertit une ligne SQL en question d'API."""
    return QuestionOut(
        id=row["id"],
        categorie=row["categorie"],
        difficulte=row["difficulte"],
        contexte=row["contexte"],
        contraintes=json.loads(row["contraintes_json"]),
        enjeu=row["enjeu"],
        enonce=row["enonce"],
        nb_sessions=row["nb_sessions"],
    )


def _filters(categorie: Categorie | None, difficulte: Difficulte | None) -> tuple[str, list[str]]:
    """Construit la clause WHERE d'un filtre catégorie / difficulté."""
    clauses: list[str] = []
    params: list[str] = []
    if categorie is not None:
        clauses.append("q.categorie = ?")
        params.append(categorie)
    if difficulte is not None:
        clauses.append("q.difficulte = ?")
        params.append(difficulte)
    return (f"WHERE {' AND '.join(clauses)} " if clauses else ""), params


def insert_question(
    conn: sqlite3.Connection, generated: GeneratedQuestion, categorie: Categorie, level: Difficulte
) -> QuestionOut:
    """Enregistre une question générée dans la banque."""
    cursor = conn.execute(
        "INSERT INTO manager_questions "
        "(categorie, difficulte, contexte, contraintes_json, enjeu, enonce, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            categorie,
            level,
            generated.contexte,
            json.dumps(generated.contraintes, ensure_ascii=False),
            generated.enjeu,
            generated.enonce,
            _now(),
        ),
    )
    conn.commit()
    question = get_question(conn, int(cursor.lastrowid or 0))
    if question is None:
        raise RuntimeError("question introuvable après insertion")
    return question


def get_question(conn: sqlite3.Connection, question_id: int) -> QuestionOut | None:
    """Retourne une question par identifiant."""
    row = conn.execute(QUESTION_SELECT + "WHERE q.id = ?", (question_id,)).fetchone()
    return _to_question(row) if row else None


def list_questions(
    conn: sqlite3.Connection, categorie: Categorie | None, difficulte: Difficulte | None
) -> list[QuestionOut]:
    """Liste la banque, filtrable, de la plus récente à la plus ancienne."""
    where, params = _filters(categorie, difficulte)
    rows = conn.execute(QUESTION_SELECT + where + "ORDER BY q.id DESC", params).fetchall()
    return [_to_question(row) for row in rows]


def draw_question(
    conn: sqlite3.Connection, categorie: Categorie | None, difficulte: Difficulte | None
) -> QuestionOut | None:
    """Tire une question de la banque en favorisant les moins travaillées."""
    where, params = _filters(categorie, difficulte)
    row = conn.execute(
        QUESTION_SELECT + where + "ORDER BY nb_sessions ASC, RANDOM() LIMIT 1", params
    ).fetchone()
    return _to_question(row) if row else None


def recent_enonces(conn: sqlite3.Connection, categorie: Categorie, limit: int) -> list[str]:
    """Derniers énoncés d'une catégorie, pour éviter les doublons à la génération."""
    rows = conn.execute(
        "SELECT enonce FROM manager_questions WHERE categorie = ? ORDER BY id DESC LIMIT ?",
        (categorie, limit),
    ).fetchall()
    return [row["enonce"] for row in rows]


def create_session(conn: sqlite3.Connection, question_id: int) -> int:
    """Crée une session sur une question et retourne son identifiant."""
    cursor = conn.execute(
        "INSERT INTO manager_sessions (created_at, question_id) VALUES (?, ?)",
        (_now(), question_id),
    )
    conn.commit()
    return int(cursor.lastrowid or 0)


def add_answer(conn: sqlite3.Connection, session_id: int, transcription: str, duree_s: int) -> int:
    """Enregistre la réponse du candidat et retourne son identifiant."""
    question_id = conn.execute(
        "SELECT question_id FROM manager_sessions WHERE id = ?", (session_id,)
    ).fetchone()["question_id"]
    cursor = conn.execute(
        "INSERT INTO manager_answers (session_id, question_id, transcription, duree_s, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (session_id, question_id, transcription, duree_s, _now()),
    )
    conn.commit()
    return int(cursor.lastrowid or 0)


def add_followup(conn: sqlite3.Connection, session_id: int, answer_id: int, texte: str) -> None:
    """Enregistre la relance du manager après une réponse."""
    conn.execute(
        "INSERT INTO manager_followups (session_id, answer_id, texte, created_at) "
        "VALUES (?, ?, ?, ?)",
        (session_id, answer_id, texte, _now()),
    )
    conn.commit()


def save_feedback(conn: sqlite3.Connection, session_id: int, feedback: Feedback) -> None:
    """Enregistre le retour (rattaché à la dernière réponse) et clôt la session."""
    last = conn.execute(
        "SELECT id FROM manager_answers WHERE session_id = ? ORDER BY id DESC LIMIT 1",
        (session_id,),
    ).fetchone()
    conn.execute(
        "INSERT INTO manager_feedbacks (answer_id, feedback_json, created_at) VALUES (?, ?, ?)",
        (last["id"], feedback.model_dump_json(), _now()),
    )
    conn.execute("UPDATE manager_sessions SET statut = 'terminee' WHERE id = ?", (session_id,))
    conn.commit()


def _feedback_json(conn: sqlite3.Connection, session_id: int) -> str | None:
    """JSON du retour d'une session, s'il existe."""
    row = conn.execute(
        "SELECT f.feedback_json FROM manager_feedbacks f "
        "JOIN manager_answers a ON a.id = f.answer_id WHERE a.session_id = ?",
        (session_id,),
    ).fetchone()
    return str(row["feedback_json"]) if row else None


def _turns(conn: sqlite3.Connection, session_id: int) -> list[Turn]:
    """Échanges de la session dans l'ordre : réponse, relance, réponse, ..."""
    rows = conn.execute(
        "SELECT a.id, a.transcription, a.duree_s, a.created_at, "
        "f.texte AS relance, f.created_at AS relance_at "
        "FROM manager_answers a LEFT JOIN manager_followups f ON f.answer_id = a.id "
        "WHERE a.session_id = ? ORDER BY a.id",
        (session_id,),
    ).fetchall()
    turns: list[Turn] = []
    for row in rows:
        turns.append(
            Turn(
                kind="answer",
                texte=row["transcription"],
                duree_s=row["duree_s"],
                created_at=row["created_at"],
            )
        )
        if row["relance"]:
            turns.append(
                Turn(
                    kind="relance", texte=row["relance"], duree_s=None, created_at=row["relance_at"]
                )
            )
    return turns


def get_session(conn: sqlite3.Connection, session_id: int) -> SessionOut | None:
    """Retourne une session complète."""
    row = conn.execute(
        "SELECT id, created_at, statut, question_id FROM manager_sessions WHERE id = ?",
        (session_id,),
    ).fetchone()
    if row is None or row["question_id"] is None:
        return None
    question = get_question(conn, row["question_id"])
    if question is None:
        return None
    turns = _turns(conn, session_id)
    raw_feedback = _feedback_json(conn, session_id)
    return SessionOut(
        id=row["id"],
        created_at=row["created_at"],
        statut=row["statut"],
        question=question,
        turns=turns,
        answers_count=sum(t.kind == "answer" for t in turns),
        max_answers=MAX_ANSWERS,
        feedback=Feedback.model_validate_json(raw_feedback) if raw_feedback else None,
    )


def list_session_summaries(conn: sqlite3.Connection) -> list[SessionSummary]:
    """Historique des sessions, de la plus récente à la plus ancienne."""
    rows = conn.execute(
        "SELECT s.id, s.created_at, s.statut, q.categorie, q.difficulte, q.enonce, "
        "(SELECT f.feedback_json FROM manager_feedbacks f "
        " JOIN manager_answers a ON a.id = f.answer_id WHERE a.session_id = s.id) AS feedback_json "
        "FROM manager_sessions s JOIN manager_questions q ON q.id = s.question_id "
        "ORDER BY s.id DESC"
    ).fetchall()
    summaries: list[SessionSummary] = []
    for row in rows:
        notes: Notes | None = (
            Feedback.model_validate_json(row["feedback_json"]).notes
            if row["feedback_json"]
            else None
        )
        summaries.append(
            SessionSummary(
                id=row["id"],
                created_at=row["created_at"],
                statut=row["statut"],
                categorie=row["categorie"],
                difficulte=row["difficulte"],
                enonce=row["enonce"],
                notes=notes,
                moyenne=notes.average() if notes else None,
            )
        )
    return summaries
