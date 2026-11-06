import type { Feedback, Question, Session, SessionSummary } from "../types";

export const QUESTION: Question = {
  id: 1,
  categorie: "decisions",
  difficulte: "moyenne",
  contexte: "Ton équipe doit lancer un assistant interne.",
  contraintes: ["Deux semaines", "GPU limités"],
  enjeu: "Une démo devant la direction.",
  enonce: "Lances-tu le modèle malgré une évaluation incertaine ?",
  lang: "fr",
  nb_sessions: 0,
};

export const FEEDBACK: Feedback = {
  points_forts: ["Structure claire"],
  points_faibles: ["Peu de chiffres"],
  oublis: ["Plan de repli"],
  notes: {
    clarte_structure: 4,
    jugement_ambiguite: 3,
    capacite_trancher: 4,
    communication_parties_prenantes: 2,
    profondeur_technique: 3,
  },
  reponse_amelioree: {
    decision: "Je commencerais par cadrer le risque.",
    actions: ["Je mesure sur 5 % du trafic."],
    compromis: ["Je sacrifie la couverture."],
    parties_prenantes: ["J'informe le comité."],
  },
  conseils: ["Chiffre le risque", "Annonce ta décision en premier"],
};

export const SESSION: Session = {
  id: 7,
  created_at: "2026-11-02T10:00:00+00:00",
  statut: "en_cours",
  question: QUESTION,
  turns: [],
  answers_count: 0,
  max_answers: 3,
  feedback: null,
};

export const ANSWERED: Session = {
  ...SESSION,
  answers_count: 1,
  turns: [{ kind: "answer", texte: "Je lance en périmètre réduit.", duree_s: 125, created_at: "t1" }],
};

export const WITH_RELANCE: Session = {
  ...ANSWERED,
  turns: [
    ...ANSWERED.turns,
    { kind: "relance", texte: "Que ferais-tu si le client refuse ?", duree_s: null, created_at: "t2" },
  ],
};

export const FINISHED: Session = { ...WITH_RELANCE, statut: "terminee", feedback: FEEDBACK };

export const SUMMARY: SessionSummary = {
  id: 7,
  created_at: "2026-11-02T10:00:00+00:00",
  statut: "terminee",
  categorie: "decisions",
  difficulte: "moyenne",
  enonce: QUESTION.enonce,
  notes: FEEDBACK.notes,
  moyenne: 3.2,
};
