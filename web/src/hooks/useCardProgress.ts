import { useState } from "react";
import { setProgress } from "../api";
import { useI18n } from "../i18n";
import type { Card, Statut } from "../types";

interface CardProgress {
  pendingId: number | null;
  error: string | null;
  update: (card: Card, statut: Statut | null) => Promise<void>;
}

type SaveProgress = (cardId: number, statut: Statut | null) => Promise<void>;

/** Enregistre le statut d'une carte (par défaut celui des Cours) et prévient le parent une fois sauvegardé. */
export function useCardProgress(
  onSaved: (card: Card, statut: Statut | null) => void,
  save: SaveProgress = setProgress,
): CardProgress {
  const { t } = useI18n();
  const [pendingId, setPendingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const update = async (card: Card, statut: Statut | null): Promise<void> => {
    setPendingId(card.id);
    setError(null);
    try {
      await save(card.id, statut);
      onSaved(card, statut);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("progress.saveFailed"));
    } finally {
      setPendingId(null);
    }
  };

  return { pendingId, error, update };
}
