import type { TKey } from "./i18n";

export const SESSION_MINUTES = 45;
export const SESSION_SECONDS = SESSION_MINUTES * 60;

/** Étapes conseillées de l'entretien (clé de traduction), avec la minute de début indicative. */
export const PHASES: { label: TKey; startMinute: number }[] = [
  { label: "phase.clarify", startMinute: 0 },
  { label: "phase.assumptions", startMinute: 5 },
  { label: "phase.diagram", startMinute: 10 },
  { label: "phase.zoom", startMinute: 25 },
  { label: "phase.tradeoffs", startMinute: 35 },
  { label: "phase.evaluation", startMinute: 40 },
  { label: "phase.conclusion", startMinute: 43 },
];

/** Index de l'étape conseillée pour un temps écoulé donné (en secondes). */
export function currentPhaseIndex(elapsedS: number): number {
  const minutes = elapsedS / 60;
  let index = 0;
  PHASES.forEach((phase, i) => {
    if (minutes >= phase.startMinute) index = i;
  });
  return index;
}
