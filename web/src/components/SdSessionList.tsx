import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listSdSessions } from "../api";
import { useI18n } from "../i18n";
import { formatDuration } from "../managerLabels";
import type { SdSessionSummary } from "../types";
import EmptyState from "./EmptyState";

const formatDate = (iso: string, locale: string): string =>
  new Date(iso).toLocaleDateString(locale, { day: "2-digit", month: "short", year: "numeric" });

interface SdSessionListProps {
  title: string;
  /** Texte de l'état vide. */
  emptyHint: string;
}

/** Sessions de System Design à rouvrir (en cours ou terminées). */
export default function SdSessionList({ title, emptyHint }: SdSessionListProps) {
  const { t, locale } = useI18n();
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
      {!error && !sessions && <p className="muted">{t("common.loading")}</p>}
      {sessions && sessions.length === 0 && <EmptyState title={t("common.noSession")} hint={emptyHint} />}
      {sessions && sessions.length > 0 && (
        <ul className="session-list">
          {sessions.map((s) => (
            <li key={s.id} className="card">
              <Link to={`/system-design/sessions/${s.id}`}>{s.titre}</Link>
              <p className="muted">
                {formatDate(s.created_at, locale)} · {t("sd.messages", { n: s.nb_messages })} ·{" "}
                {formatDuration(s.elapsed_s)}
                {` · ${s.statut === "en_cours" ? t("sd.inProgress") : t("sd.finished")}`}
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
