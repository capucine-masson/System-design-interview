-- Cours : traductions des thèmes et des cartes (le français reste dans themes et cards)
CREATE TABLE theme_translations (
    theme_id INTEGER NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    lang TEXT NOT NULL CHECK (lang IN ('fr', 'en')),
    titre TEXT NOT NULL,
    source_label TEXT,
    PRIMARY KEY (theme_id, lang)
);

CREATE TABLE card_translations (
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    lang TEXT NOT NULL CHECK (lang IN ('fr', 'en')),
    titre TEXT NOT NULL,
    explication_orale TEXT NOT NULL,
    points_json TEXT NOT NULL,
    schema TEXT,
    source_label TEXT,
    PRIMARY KEY (card_id, lang)
);
