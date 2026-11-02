-- Cours : slug et source par thème, points clés et source par carte
ALTER TABLE themes ADD COLUMN slug TEXT;
ALTER TABLE themes ADD COLUMN source_label TEXT;
ALTER TABLE themes ADD COLUMN source_url TEXT;

ALTER TABLE cards ADD COLUMN points_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE cards ADD COLUMN source_label TEXT;

CREATE UNIQUE INDEX idx_themes_slug ON themes(slug);
CREATE UNIQUE INDEX idx_cards_theme_titre ON cards(theme_id, titre);
