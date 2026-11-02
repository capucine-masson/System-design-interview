import type { Categorie, Difficulte, Notes } from "./types";

export const CATEGORIES: { value: Categorie; label: string }[] = [
  { value: "mixte", label: "Mixte" },
  { value: "ambiguite", label: "Ambiguïté" },
  { value: "decisions", label: "Décisions difficiles" },
  { value: "parties_prenantes", label: "Parties prenantes" },
  { value: "technique", label: "Technique" },
  { value: "comportemental", label: "Comportemental" },
];

export const DIFFICULTES: { value: Difficulte; label: string }[] = [
  { value: "facile", label: "Facile" },
  { value: "moyenne", label: "Moyenne" },
  { value: "difficile", label: "Difficile" },
];

export const CRITERIA: { key: keyof Notes; label: string; short: string }[] = [
  { key: "clarte_structure", label: "Clarté et structure", short: "Clarté" },
  { key: "jugement_ambiguite", label: "Jugement face à l'ambiguïté", short: "Ambiguïté" },
  { key: "capacite_trancher", label: "Capacité à trancher", short: "Trancher" },
  {
    key: "communication_parties_prenantes",
    label: "Communication avec les parties prenantes",
    short: "Parties prenantes",
  },
  { key: "profondeur_technique", label: "Profondeur technique", short: "Technique" },
];

export const MAX_NOTE = 5;
export const MAX_ANSWER_CHARS = 4000;
export const TARGET_MIN_S = 120;
export const TARGET_MAX_S = 180;

export const categorieLabel = (value: Categorie): string =>
  CATEGORIES.find((c) => c.value === value)?.label ?? value;

export const difficulteLabel = (value: Difficulte): string =>
  DIFFICULTES.find((d) => d.value === value)?.label ?? value;

export function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}
