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
}
