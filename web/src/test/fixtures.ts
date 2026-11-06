import type { Card, CourseReview, Theme } from "../types";

export const REVIEW: CourseReview = {
  verdict: "partiel",
  points_justes: ["Tu as parlé du softmax."],
  points_manquants: ["Les projections Q, K, V."],
  erreurs: [],
  details: ["Q, K et V viennent de trois projections apprises."],
  explication_simple: "Chaque mot regarde les autres et choisit ceux qui comptent.",
};

export const CARD: Card = {
  id: 1,
  theme_slug: "transformers",
  titre: "Self-attention",
  accroche: "Chaque token pondère les autres.",
  points: ["Q, K et V sont des projections.", "On applique un softmax.", "On somme les valeurs."],
  diagram: {
    nodes: [
      { id: "a", label: "Entrée", col: 0, row: 0 },
      { id: "b", label: "Sortie", col: 1, row: 0 },
    ],
    edges: [{ source: "a", target: "b", label: null }],
  },
  source_label: "The Illustrated Transformer",
  source_url: "https://example.org/source",
  statut: null,
  essentielle: false,
};

export const CARD_2: Card = { ...CARD, id: 2, titre: "Tokenisation", diagram: null, statut: "a_revoir" };

export const THEME: Theme = {
  slug: "transformers",
  titre: "Transformers",
  source_label: "The Illustrated Transformer",
  source_url: "https://example.org/source",
  total: 2,
  maitrisees: 1,
  a_revoir: 1,
  fait: false,
};
