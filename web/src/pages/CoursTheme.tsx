import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCards, getThemes } from "../api";
import EmptyState from "../components/EmptyState";
import FlipCard from "../components/FlipCard";
import ProgressBar from "../components/ProgressBar";
import { useCardProgress } from "../hooks/useCardProgress";
import { useI18n } from "../i18n";
import type { Card, Statut, Theme } from "../types";

export default function CoursTheme() {
  const { lang, t } = useI18n();
  const { slug = "" } = useParams();
  const [theme, setTheme] = useState<Theme | null>(null);
  const [cards, setCards] = useState<Card[] | null>(null);
  const [onlyToReview, setOnlyToReview] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshTheme = useCallback(
    () =>
      getThemes()
        .then((themes) => setTheme(themes.find((t) => t.slug === slug) ?? null))
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
    getCards(slug, statut)
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
  });

  return (
    <section>
      <p>
        <Link to="/cours" className="muted">
          {t("courses.allThemes")}
        </Link>
      </p>
      <div className="page-head">
        <h1>{theme?.titre ?? t("courses.themeFallback")}</h1>
        <Link to={`/cours/revision?theme=${encodeURIComponent(slug)}`} className="btn btn-primary">
          {t("courses.reviewTheme")}
        </Link>
      </div>
      {theme && (
        <div className="theme-meta">
          <ProgressBar maitrisees={theme.maitrisees} aRevoir={theme.a_revoir} total={theme.total} />
          {theme.source_label && (
            <p className="muted">
              {t("common.source")}{" "}
              {theme.source_url ? (
                <a href={theme.source_url} target="_blank" rel="noreferrer">
                  {theme.source_label}
                </a>
              ) : (
                theme.source_label
              )}
            </p>
          )}
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
          hint={onlyToReview ? t("courses.nothingToReviewHint") : t("courses.noCardsHint")}
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
