"""Correction d'une session de System Design : solution de référence (en cache) et verdict."""

import sqlite3

from fastapi import HTTPException

from api import sd_db
from api.config import Settings
from api.course_models import Diagram, DiagramEdge, DiagramNode
from api.llm import LLMClient, complete_json, correction_messages, reference_messages
from api.scene_text import describe_scene, render_text
from api.sd import HTTP_CONFLICT, HTTP_NOT_FOUND, require_session
from api.sd_catalog import get_case_type
from api.sd_correction_models import (
    CorrectionBundle,
    HiddenDetailStatus,
    RefDiagram,
    ReferenceOut,
    ReferenceSolution,
    SdCorrection,
)

FEATURE_REFERENCE = "sd_reference"
FEATURE_CORRECTION = "sd_correction"

TOKENS_REFERENCE = 2200
TOKENS_CORRECTION = 1500
TEMPERATURE_REFERENCE = 0.4
TEMPERATURE_CORRECTION = 0.2

MAX_NODE_LABEL = 40
MAX_EDGE_LABEL = 24


def _normalize(text: str) -> str:
    """Forme comparable d'un libellé (casse, espaces)."""
    return " ".join(text.casefold().split())


def to_diagram(schema: RefDiagram) -> Diagram | None:
    """Convertit le schéma du LLM en diagramme sûr (libellés tronqués, liens valides)."""
    nodes: list[DiagramNode] = []
    taken: set[tuple[int, int]] = set()
    for raw in schema.noeuds:
        node_id, label = raw.id.strip(), raw.label.strip()[:MAX_NODE_LABEL]
        if not node_id or not label or any(n.id == node_id for n in nodes):
            continue
        col, row = max(0, raw.col), max(0, raw.row)
        while (col, row) in taken:
            row += 1  # deux boîtes ne partagent jamais la même case
        taken.add((col, row))
        nodes.append(DiagramNode(id=node_id, label=label, col=col, row=row))
    if len(nodes) < 2:
        return None
    ids = {n.id for n in nodes}
    edges = [
        DiagramEdge(
            source=link.source.strip(),
            target=link.cible.strip(),
            label=link.label.strip()[:MAX_EDGE_LABEL] or None,
        )
        for link in schema.liens
        if link.source.strip() in ids and link.cible.strip() in ids
    ]
    return Diagram(nodes=nodes, edges=edges)


def _reference_out(reference: ReferenceSolution) -> ReferenceOut:
    return ReferenceOut(
        hypotheses=reference.hypotheses,
        dimensionnement=reference.dimensionnement,
        composants=reference.composants,
        flux=reference.flux,
        compromis=reference.compromis,
        evaluation_monitoring=reference.evaluation_monitoring,
        pieges=reference.pieges,
        diagramme=to_diagram(reference.diagramme),
    )


def _bundle(
    conn: sqlite3.Connection, case_id: int, correction: SdCorrection, reference: ReferenceSolution
) -> CorrectionBundle:
    """Assemble la réponse : moyenne et détails révélés calculés en code."""
    found = {_normalize(subject) for subject in correction.details_decouverts}
    details = [
        HiddenDetailStatus(sujet=d.sujet, valeur=d.valeur, decouvert=_normalize(d.sujet) in found)
        for d in sd_db.get_hidden(conn, case_id).details
    ]
    return CorrectionBundle(
        correction=correction,
        moyenne=correction.notes.average(),
        details=details,
        reference=_reference_out(reference),
    )


def _require_finished(conn: sqlite3.Connection, session_id: int) -> int:
    """Retourne l'identifiant du cas si la session est terminée (sinon 409)."""
    session = require_session(conn, session_id)
    if session.statut != "terminee":
        raise HTTPException(HTTP_CONFLICT, "Termine d'abord la session pour voir la correction.")
    return session.case.id


def get_correction(conn: sqlite3.Connection, session_id: int) -> CorrectionBundle:
    """Correction déjà générée (aucun appel IA) ; 404 si elle n'existe pas encore."""
    case_id = _require_finished(conn, session_id)
    correction = sd_db.get_correction(conn, session_id)
    reference = sd_db.get_reference(conn, case_id)
    if correction is None or reference is None:
        raise HTTPException(HTTP_NOT_FOUND, "Pas encore de correction pour cette session.")
    return _bundle(conn, case_id, correction, reference)


def _ensure_reference(
    conn: sqlite3.Connection, settings: Settings, client: LLMClient, case_id: int
) -> ReferenceSolution:
    """Solution de référence du cas : relue du cache, sinon générée une seule fois."""
    cached = sd_db.get_reference(conn, case_id)
    if cached is not None:
        return cached
    case = sd_db.get_case(conn, case_id)
    case_type = get_case_type(case.type) if case else None
    if case is None or case_type is None:
        raise HTTPException(HTTP_NOT_FOUND, "Cas introuvable.")
    reference = complete_json(
        conn,
        settings,
        client,
        FEATURE_REFERENCE,
        reference_messages(case_type, case.brief, sd_db.get_hidden(conn, case_id)),
        ReferenceSolution,
        TOKENS_REFERENCE,
        TEMPERATURE_REFERENCE,
    )
    sd_db.save_reference(conn, case_id, reference)
    return reference


def request_correction(
    conn: sqlite3.Connection, settings: Settings, client: LLMClient, session_id: int
) -> CorrectionBundle:
    """Produit la correction (jusqu'à 2 appels IA, 0 si déjà faite) d'une session terminée."""
    case_id = _require_finished(conn, session_id)
    existing = sd_db.get_correction(conn, session_id)
    reference = _ensure_reference(conn, settings, client, case_id)
    if existing is not None:
        return _bundle(conn, case_id, existing, reference)
    session = require_session(conn, session_id)
    scene = sd_db.get_scene(conn, session_id, None)
    scene_text = render_text(describe_scene(scene.elements if scene else []))
    correction = complete_json(
        conn,
        settings,
        client,
        FEATURE_CORRECTION,
        correction_messages(
            session.case.brief,
            sd_db.get_hidden(conn, case_id),
            reference,
            session.messages,
            scene_text,
            session.elapsed_s,
        ),
        SdCorrection,
        TOKENS_CORRECTION,
        TEMPERATURE_CORRECTION,
    )
    sd_db.save_correction(conn, session_id, correction)
    return _bundle(conn, case_id, correction, reference)
