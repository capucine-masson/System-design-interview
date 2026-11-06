-- Langue (fr/en) des cas de system design et des questions manager déjà en banque
ALTER TABLE sd_cases ADD COLUMN lang TEXT NOT NULL DEFAULT 'fr' CHECK (lang IN ('fr', 'en'));
ALTER TABLE manager_questions ADD COLUMN lang TEXT NOT NULL DEFAULT 'fr'
    CHECK (lang IN ('fr', 'en'));
