import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listSessions } from "../api";
import { categorieLabel, CRITERIA, difficulteLabel } from "../managerLabels";
import type { SessionSummary } from "../types";
import EmptyState from "./EmptyState";
import ScoreChart from "./ScoreChart";

const DECIMALS = 1;
const MAX_ENONCE_CHARS = 90;

const formatDate = (iso: string): string =>
  new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });

const shorten = (text: string): string =>
  text.length > MAX_ENONCE_CHARS ? `${text.slice(0, MAX_ENONCE_CHARS).trimEnd()}…` : text;

export default function ManagerHistory() {
  const [sessions, setSessions] = useState<SessionSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSessions()
      .then(setSessions)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section aria-label="Historique de l'entretien manager">
      <h2>Entretien manager</h2>
      {error && <div className="notice notice-error">{error}</div>}
      {!error && !sessions && <p className="muted">Chargement…</p>}
      {sessions && sessions.length === 0 && (
        <EmptyState
          title="Aucune session"
          hint="Fais ton premier entretien : il apparaîtra ici, avec tes notes."
        />
      )}
      {sessions && sessions.length > 0 && (
        <>
          <div className="card">
            <h3>Évolution de la moyenne</h3>
            <ScoreChart sessions={sessions} />
          </div>
          <div className="card table-wrap">
            <table className="table history-table">
              <thead>
                <tr>
                  <th>Session</th>
                  <th>Moy.</th>
                  {CRITERIA.map((criterion) => (
                    <th key={criterion.key}>{criterion.short}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sessions.map((s) => (
                  <tr key={s.id}>
                    <td>
                      <Link to={`/entretien-manager/sessions/${s.id}`}>{shorten(s.enonce)}</Link>
                      <div className="muted">
                        {formatDate(s.created_at)} · {categorieLabel(s.categorie)} ·{" "}
                        {difficulteLabel(s.difficulte)}
                        {s.statut === "en_cours" ? " · en cours" : ""}
                      </div>
                    </td>
                    <td>{s.moyenne === null ? "–" : s.moyenne.toFixed(DECIMALS)}</td>
                    {CRITERIA.map((criterion) => (
                      <td key={criterion.key}>{s.notes ? s.notes[criterion.key] : "–"}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
