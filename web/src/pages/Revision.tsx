import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getRandomCard } from "../api";
import EmptyState from "../components/EmptyState";
import FlipCard from "../components/FlipCard";
import { useCardProgress } from "../hooks/useCardProgress";
import type { Card } from "../types";

export default function Revision() {
  const [params] = useSearchParams();
  const theme = params.get("theme") ?? undefined;
  const [onlyToReview, setOnlyToReview] = useState(false);
  const [card, setCard] = useState<Card | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const draw = useCallback(
    async (exclude?: number): Promise<void> => {
      setLoading(true);
      setError(null);
      try {
        setCard(await getRandomCard({ theme, statut: onlyToReview ? "a_revoir" : undefined, exclude }));
      } catch (err) {
        setCard(null);
        setError(err instanceof Error ? err.message : "Échec du tirage.");
      } finally {
        setLoading(false);
      }
    },
    [theme, onlyToReview],
  );

  useEffect(() => {
    void draw();
  }, [draw]);

  const progress = useCardProgress((saved, statut) =>
    setCard((current) => (current && current.id === saved.id ? { ...current, statut } : current)),
  );

  return (
    <section>
      <p>
        <Link to={theme ? `/cours/${theme}` : "/cours"} className="muted">
          ← Retour
        </Link>
      </p>
      <div className="page-head">
        <h1>Révision aléatoire</h1>
        <button type="button" className="btn btn-primary" disabled={loading} onClick={() => void draw(card?.id)}>
          Carte suivante
        </button>
      </div>
      <div className="toolbar">
        <button
          type="button"
          className="btn"
          aria-pressed={onlyToReview}
          onClick={() => setOnlyToReview((value) => !value)}
        >
          {onlyToReview ? "Toutes les cartes" : "Seulement « à revoir »"}
        </button>
      </div>
      {progress.error && <div className="card error">{progress.error}</div>}
      {loading && <p className="muted">Tirage…</p>}
      {!loading && error && (
        <EmptyState
          title={onlyToReview ? "Rien à revoir" : "Aucune carte"}
          hint={error}
        />
      )}
      {!loading && card && (
        <div className="revision-card">
          <FlipCard
            key={card.id}
            card={card}
            pending={progress.pendingId === card.id}
            onProgress={progress.update}
          />
        </div>
      )}
    </section>
  );
}
