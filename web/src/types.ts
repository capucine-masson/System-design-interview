import type { Lang } from "./i18n";

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
  /** Coche manuelle : « je pense maîtriser ce thème ». */
  fait: boolean;
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

export type RevisionCount = 5 | 10 | "max";

export type Verdict = "correct" | "partiel" | "faux";

export interface CourseReview {
  verdict: Verdict;
  points_justes: string[];
  points_manquants: string[];
  erreurs: string[];
  details: string[];
  explication_simple: string;
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
  lang: Lang;
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

export type CaseFamily = "ml" | "classique";

export interface CaseType {
  slug: string;
  famille: CaseFamily;
  titre: string;
  description: string;
}

export interface SdCase {
  id: number;
  type: string;
  titre: string;
  brief: string;
  lang: Lang;
  nb_sessions: number;
}

export interface SdMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface SdSession {
  id: number;
  created_at: string;
  statut: "en_cours" | "terminee";
  elapsed_s: number;
  case: SdCase;
  messages: SdMessage[];
  user_messages: number;
  max_user_messages: number;
  awaiting_reply: boolean;
}

export interface SdSessionSummary {
  id: number;
  created_at: string;
  statut: "en_cours" | "terminee";
  type: string;
  titre: string;
  nb_messages: number;
  elapsed_s: number;
}

export interface SceneVersion {
  version: number;
  created_at: string;
}

/** Éléments Excalidraw sérialisés (JSON), tels que stockés par le serveur. */
export type SceneElement = Record<string, unknown>;

export interface StoredScene extends SceneVersion {
  elements: SceneElement[];
  app_state: Record<string, unknown>;
}

export interface SdNotes {
  clarification: number;
  hypotheses: number;
  architecture: number;
  approfondissement: number;
  compromis: number;
  evaluation_monitoring: number;
}

export interface SdCorrection {
  resume: string;
  notes: SdNotes;
  details_decouverts: string[];
  points_forts: string[];
  points_faibles: string[];
  composants_manquants: string[];
  conseils: string[];
}

export interface RefComponent {
  nom: string;
  role: string;
}

export interface RefTradeoff {
  choix: string;
  alternative: string;
  raison: string;
}

export interface SdReference {
  hypotheses: string[];
  dimensionnement: string[];
  composants: RefComponent[];
  flux: string[];
  compromis: RefTradeoff[];
  evaluation_monitoring: string[];
  pieges: string[];
  diagramme: Diagram | null;
}

export interface HiddenDetailStatus {
  sujet: string;
  valeur: string;
  decouvert: boolean;
}

export interface CorrectionBundle {
  correction: SdCorrection;
  moyenne: number;
  details: HiddenDetailStatus[];
  reference: SdReference;
}
