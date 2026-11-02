import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listSdSessions } from "../api";
import { formatDuration } from "../managerLabels";
import type { SdSessionSummary } from "../types";
import EmptyState from "./EmptyState";

const formatDate = (iso: string): string =>
  new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });

interface SdSessionListProps {
  title: string;
  /** Texte de l'état vide. */
  emptyHint: string;
}

/** Sessions de System Design à rouvrir (en cours ou terminées). */
export default function SdSessionList({ title, emptyHint }: SdSessionListProps) {
  const [sessions, setSessions] = useState<SdSessionSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSdSessions()
      .then(setSessions)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section aria-label={title}>
      <h2>{title}</h2>
      {error && <div className="notice notice-error">{error}</div>}
      {!error && !sessions && <p className="muted">Chargement…</p>}
      {sessions && sessions.length === 0 && <EmptyState title="Aucune session" hint={emptyHint} />}
      {sessions && sessions.length > 0 && (
        <ul className="session-list">
          {sessions.map((s) => (
            <li key={s.id} className="card">
              <Link to={`/system-design/sessions/${s.id}`}>{s.titre}</Link>
              <p className="muted">
                {formatDate(s.created_at)} · {s.nb_messages} messages · {formatDuration(s.elapsed_s)}
                {s.statut === "en_cours" ? " · en cours" : " · terminée"}
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
