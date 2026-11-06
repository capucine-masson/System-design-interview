import type { TKey, Translate } from "./i18n";
import type { Categorie, Difficulte, Notes } from "./types";

export const CATEGORIES: Categorie[] = [
  "mixte",
  "ambiguite",
  "decisions",
  "parties_prenantes",
  "technique",
  "comportemental",
];

export const DIFFICULTES: Difficulte[] = ["facile", "moyenne", "difficile"];

const CRITERIA_KEYS: (keyof Notes)[] = [
  "clarte_structure",
  "jugement_ambiguite",
  "capacite_trancher",
  "communication_parties_prenantes",
  "profondeur_technique",
];

/** Critères de notation, avec les clés de traduction du libellé complet et du libellé court. */
export const CRITERIA: { key: keyof Notes; label: TKey; short: TKey }[] = CRITERIA_KEYS.map(
  (key) => ({ key, label: `manager.criterion.${key}`, short: `manager.short.${key}` }),
);

export const MAX_NOTE = 5;
export const MAX_ANSWER_CHARS = 4000;
export const TARGET_MIN_S = 120;
export const TARGET_MAX_S = 180;

export const categorieLabel = (value: Categorie, t: Translate): string =>
  t(`manager.cat.${value}`);

export const difficulteLabel = (value: Difficulte, t: Translate): string =>
  t(`manager.level.${value}`);

export function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}
