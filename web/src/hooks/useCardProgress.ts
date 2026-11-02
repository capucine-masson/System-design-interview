import { useState } from "react";
import { setProgress } from "../api";
import type { Card, Statut } from "../types";

interface CardProgress {
  pendingId: number | null;
  error: string | null;
  update: (card: Card, statut: Statut | null) => Promise<void>;
}

/** Enregistre le statut d'une carte en base et prévient le parent une fois sauvegardé. */
export function useCardProgress(onSaved: (card: Card, statut: Statut | null) => void): CardProgress {
  const [pendingId, setPendingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const update = async (card: Card, statut: Statut | null): Promise<void> => {
    setPendingId(card.id);
    setError(null);
    try {
      await setProgress(card.id, statut);
      onSaved(card, statut);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec de la sauvegarde.");
    } finally {
      setPendingId(null);
    }
  };

  return { pendingId, error, update };
}
