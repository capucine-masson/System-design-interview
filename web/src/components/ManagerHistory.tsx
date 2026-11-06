import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listSessions } from "../api";
import { useI18n } from "../i18n";
import { categorieLabel, CRITERIA, difficulteLabel } from "../managerLabels";
import type { SessionSummary } from "../types";
import EmptyState from "./EmptyState";

const DECIMALS = 1;
const MAX_ENONCE_CHARS = 90;

const formatDate = (iso: string, locale: string): string =>
  new Date(iso).toLocaleDateString(locale, { day: "2-digit", month: "short", year: "numeric" });

const shorten = (text: string): string =>
  text.length > MAX_ENONCE_CHARS ? `${text.slice(0, MAX_ENONCE_CHARS).trimEnd()}…` : text;

export default function ManagerHistory() {
  const { t, locale } = useI18n();
  const [sessions, setSessions] = useState<SessionSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSessions()
      .then(setSessions)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section aria-label={t("history.managerAria")}>
      <h2>{t("manager.title")}</h2>
      {error && <div className="notice notice-error">{error}</div>}
      {!error && !sessions && <p className="muted">{t("common.loading")}</p>}
      {sessions && sessions.length === 0 && (
        <EmptyState
          title={t("common.noSession")}
          hint={t("history.noSessionHint")}
        />
      )}
      {sessions && sessions.length > 0 && (
        <>
          <div className="card table-wrap">
            <table className="table history-table">
              <thead>
                <tr>
                  <th>{t("history.colSession")}</th>
                  <th>{t("history.colAverage")}</th>
                  {CRITERIA.map((criterion) => (
                    <th key={criterion.key}>{t(criterion.short)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sessions.map((s) => (
                  <tr key={s.id}>
                    <td>
                      <Link to={`/entretien-manager/sessions/${s.id}`}>{shorten(s.enonce)}</Link>
                      <div className="muted">
                        {formatDate(s.created_at, locale)} · {categorieLabel(s.categorie, t)} ·{" "}
                        {difficulteLabel(s.difficulte, t)}
                        {s.statut === "en_cours" ? ` · ${t("history.inProgress")}` : ""}
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
