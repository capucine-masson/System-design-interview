import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getWorkflowCards, getWorkflowThemes, setWorkflowProgress } from "../api";
import EmptyState from "../components/EmptyState";
import FlipCard from "../components/FlipCard";
import ProgressBar from "../components/ProgressBar";
import { useCardProgress } from "../hooks/useCardProgress";
import { useI18n } from "../i18n";
import type { Card, Statut, Theme } from "../types";

export default function WorkflowsTheme() {
  const { lang, t } = useI18n();
  const { slug = "" } = useParams();
  const [theme, setTheme] = useState<Theme | null>(null);
  const [cards, setCards] = useState<Card[] | null>(null);
  const [onlyToReview, setOnlyToReview] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshTheme = useCallback(
    () =>
      getWorkflowThemes()
        .then((themes) => setTheme(themes.find((item) => item.slug === slug) ?? null))
        .catch((err: Error) => setError(err.message)),
    [slug, lang],
  );

  useEffect(() => {
    void refreshTheme();
  }, [refreshTheme]);

  useEffect(() => {
    setCards(null);
    setError(null);
    const statut: Statut | undefined = onlyToReview ? "a_revoir" : undefined;
    getWorkflowCards(slug, statut)
      .then(setCards)
      .catch((err: Error) => setError(err.message));
  }, [slug, onlyToReview, lang]);

  const progress = useCardProgress((card, statut) => {
    setCards((current) =>
      (current ?? [])
        .map((c) => (c.id === card.id ? { ...c, statut } : c))
        .filter((c) => !onlyToReview || c.statut === "a_revoir"),
    );
    void refreshTheme();
  }, setWorkflowProgress);

  return (
    <section>
      <p>
        <Link to="/workflows" className="muted">
          {t("workflows.allThemes")}
        </Link>
      </p>
      <div className="page-head">
        <h1>{theme?.titre ?? t("workflows.themeFallback")}</h1>
        <Link
          to={`/workflows/revision?theme=${encodeURIComponent(slug)}`}
          className="btn btn-primary"
        >
          {t("workflows.reviewTheme")}
        </Link>
      </div>
      {theme && (
        <div className="theme-meta">
          <ProgressBar maitrisees={theme.maitrisees} aRevoir={theme.a_revoir} total={theme.total} />
        </div>
      )}
      <div className="toolbar">
        <button
          type="button"
          className="btn"
          aria-pressed={onlyToReview}
          onClick={() => setOnlyToReview((value) => !value)}
        >
          {onlyToReview ? t("courses.showAll") : t("courses.filterToReview")}
        </button>
      </div>
      {progress.error && <div className="card error">{progress.error}</div>}
      {error && <div className="card error">{error}</div>}
      {!error && !cards && <p className="muted">{t("common.loading")}</p>}
      {cards && cards.length === 0 && (
        <EmptyState
          title={onlyToReview ? t("courses.nothingToReview") : t("courses.noCards")}
          hint={onlyToReview ? t("workflows.nothingToReviewHint") : t("workflows.noCardsHint")}
        />
      )}
      {cards && cards.length > 0 && (
        <div className="grid cards-grid">
          {cards.map((card) => (
            <FlipCard
              key={card.id}
              card={card}
              pending={progress.pendingId === card.id}
              onProgress={progress.update}
            />
          ))}
        </div>
      )}
    </section>
  );
}
