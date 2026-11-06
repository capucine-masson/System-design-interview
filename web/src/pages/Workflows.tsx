import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getWorkflowThemes } from "../api";
import EmptyState from "../components/EmptyState";
import ProgressBar from "../components/ProgressBar";
import { useI18n } from "../i18n";
import type { Theme } from "../types";

export default function Workflows() {
  const { lang, t } = useI18n();
  const [themes, setThemes] = useState<Theme[] | null>(null);
  const [error, setError] = useState<string | null>(null);

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
      {!error && !themes && <p className="muted">{t("common.loading")}</p>}
      {themes && themes.length === 0 && (
        <EmptyState title={t("workflows.noThemes")} hint={t("workflows.noThemesHint")} />
      )}
      {themes && themes.length > 0 && (
        <div className="grid themes-grid">
          {themes.map((theme) => (
            <Link key={theme.slug} to={`/workflows/${theme.slug}`} className="card theme-card">
              <h2>{theme.titre}</h2>
              <ProgressBar
                maitrisees={theme.maitrisees}
                aRevoir={theme.a_revoir}
                total={theme.total}
              />
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
