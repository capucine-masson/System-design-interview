export const SESSION_MINUTES = 45;
export const SESSION_SECONDS = SESSION_MINUTES * 60;

/** Étapes conseillées de l'entretien, avec la minute de début indicative. */
export const PHASES: { label: string; startMinute: number }[] = [
  { label: "Clarifier", startMinute: 0 },
  { label: "Hypothèses", startMinute: 5 },
  { label: "Schéma", startMinute: 10 },
  { label: "Zoom", startMinute: 25 },
  { label: "Compromis", startMinute: 35 },
  { label: "Évaluation et monitoring", startMinute: 40 },
  { label: "Conclusion", startMinute: 43 },
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
