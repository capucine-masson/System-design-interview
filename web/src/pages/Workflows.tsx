import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getWorkflowThemes, setWorkflowThemeDone } from "../api";
import EmptyState from "../components/EmptyState";
import ThemeTile from "../components/ThemeTile";
import { useThemeDone } from "../hooks/useThemeDone";
import { useI18n } from "../i18n";
import type { Theme } from "../types";

export default function Workflows() {
  const { lang, t } = useI18n();
  const [themes, setThemes] = useState<Theme[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const done = useThemeDone(setWorkflowThemeDone, setThemes);

  useEffect(() => {
    getWorkflowThemes()
      .then(setThemes)
      .catch((err: Error) => setError(err.message));
  }, [lang]);

  return (
    <section>
      <div className="page-head">
        <h1>{t("workflows.title")}</h1>
        {themes && themes.length > 0 && (
          <Link to="/workflows/revision" className="btn btn-primary">
            {t("courses.randomReview")}
          </Link>
        )}
      </div>
      {error && <div className="card error">{error}</div>}
      {done.error && <div className="card error">{done.error}</div>}
      {!error && !themes && <p className="muted">{t("common.loading")}</p>}
      {themes && themes.length === 0 && (
        <EmptyState title={t("workflows.noThemes")} hint={t("workflows.noThemesHint")} />
      )}
      {themes && themes.length > 0 && (
        <div className="grid themes-grid">
          {themes.map((theme) => (
            <ThemeTile
              key={theme.slug}
              theme={theme}
              to={`/workflows/${theme.slug}`}
              pending={done.pendingSlug === theme.slug}
              onToggle={(item) => void done.toggle(item)}
            />
          ))}
        </div>
      )}
    </section>
  );
}
