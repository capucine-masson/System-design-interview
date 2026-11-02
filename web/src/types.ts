export interface FeatureUsage {
  feature: string;
  calls: number;
  tokens_in: number;
  tokens_out: number;
  cost_estimate: number;
}

export interface UsageSummary {
  total: FeatureUsage;
  by_feature: FeatureUsage[];
}

export type Statut = "maitrisee" | "a_revoir";

export interface DiagramNode {
  id: string;
  label: string;
  col: number;
  row: number;
}

export interface DiagramEdge {
  source: string;
  target: string;
  label: string | null;
}

export interface Diagram {
  nodes: DiagramNode[];
  edges: DiagramEdge[];
}

export interface Theme {
  slug: string;
  titre: string;
  source_label: string | null;
  source_url: string | null;
  total: number;
  maitrisees: number;
  a_revoir: number;
}

export interface Card {
  id: number;
  theme_slug: string;
  titre: string;
  accroche: string;
  points: string[];
  diagram: Diagram | null;
  source_label: string | null;
  source_url: string | null;
  statut: Statut | null;
  essentielle: boolean;
}

export type Categorie =
  | "ambiguite"
  | "decisions"
  | "parties_prenantes"
  | "technique"
  | "comportemental"
  | "mixte";
export type Difficulte = "facile" | "moyenne" | "difficile";

export interface Question {
  id: number;
  categorie: Categorie;
  difficulte: Difficulte;
  contexte: string;
  contraintes: string[];
  enjeu: string;
  enonce: string;
  nb_sessions: number;
}

export interface Notes {
  clarte_structure: number;
  jugement_ambiguite: number;
  capacite_trancher: number;
  communication_parties_prenantes: number;
  profondeur_technique: number;
}

export interface ReponseOrale {
  decision: string;
  actions: string[];
  compromis: string[];
  parties_prenantes: string[];
}

export interface Feedback {
  points_forts: string[];
  points_faibles: string[];
  oublis: string[];
  notes: Notes;
  reponse_amelioree: ReponseOrale;
  conseils: string[];
}

export interface Turn {
  kind: "answer" | "relance";
  texte: string;
  duree_s: number | null;
  created_at: string;
}

export interface Session {
  id: number;
  created_at: string;
  statut: "en_cours" | "terminee";
  question: Question;
  turns: Turn[];
  answers_count: number;
  max_answers: number;
  feedback: Feedback | null;
}

export interface SessionSummary {
  id: number;
  created_at: string;
  statut: "en_cours" | "terminee";
  categorie: Categorie;
  difficulte: Difficulte;
  enonce: string;
  notes: Notes | null;
  moyenne: number | null;
}
