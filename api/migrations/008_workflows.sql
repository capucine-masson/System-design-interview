-- Mistral Workflows : catégories (thèmes), cartes et progression, séparées de la section Cours
CREATE TABLE wf_themes (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    titre TEXT NOT NULL,
    ordre INTEGER NOT NULL DEFAULT 0,
    source_label TEXT,
    source_url TEXT
);
CREATE TABLE wf_cards (
    id INTEGER PRIMARY KEY,
    theme_id INTEGER NOT NULL REFERENCES wf_themes(id) ON DELETE CASCADE,
    titre TEXT NOT NULL,
    explication_orale TEXT NOT NULL,
    points_json TEXT NOT NULL DEFAULT '[]',
    schema TEXT,
    source_label TEXT,
    source_url TEXT,
    essentielle INTEGER NOT NULL DEFAULT 0,
    ordre INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE wf_card_progress (
    card_id INTEGER PRIMARY KEY REFERENCES wf_cards(id) ON DELETE CASCADE,
    statut TEXT NOT NULL CHECK (statut IN ('maitrisee', 'a_revoir')),
    updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX idx_wf_cards_theme_titre ON wf_cards(theme_id, titre);
CREATE INDEX idx_wf_cards_theme ON wf_cards(theme_id, ordre);
