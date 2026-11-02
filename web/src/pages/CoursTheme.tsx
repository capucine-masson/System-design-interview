import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCards, getThemes } from "../api";
import EmptyState from "../components/EmptyState";
import FlipCard from "../components/FlipCard";
import ProgressBar from "../components/ProgressBar";
import { useCardProgress } from "../hooks/useCardProgress";
import type { Card, Statut, Theme } from "../types";

export default function CoursTheme() {
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
    [slug],
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
  }, [slug, onlyToReview]);

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
          ← Tous les thèmes
        </Link>
      </p>
      <div className="page-head">
        <h1>{theme?.titre ?? "Thème"}</h1>
        <Link to={`/cours/revision?theme=${encodeURIComponent(slug)}`} className="btn btn-primary">
          Réviser ce thème
        </Link>
      </div>
      {theme && (
        <div className="theme-meta">
          <ProgressBar maitrisees={theme.maitrisees} aRevoir={theme.a_revoir} total={theme.total} />
          {theme.source_label && (
            <p className="muted">
              Source :{" "}
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
          {onlyToReview ? "Afficher toutes les cartes" : "Filtrer : à revoir"}
        </button>
      </div>
      {progress.error && <div className="card error">{progress.error}</div>}
      {error && <div className="card error">{error}</div>}
      {!error && !cards && <p className="muted">Chargement…</p>}
      {cards && cards.length === 0 && (
        <EmptyState
          title={onlyToReview ? "Rien à revoir" : "Aucune carte"}
          hint={
            onlyToReview
              ? "Aucune carte n'est marquée « à revoir » dans ce thème."
              : "Ce thème n'a pas encore de carte."
          }
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
