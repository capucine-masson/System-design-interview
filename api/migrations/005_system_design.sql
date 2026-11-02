-- System design : titre du cas, suivi de session (temps, statut, résumé glissant), hash de scène
ALTER TABLE sd_cases ADD COLUMN titre TEXT NOT NULL DEFAULT '';

ALTER TABLE sd_sessions ADD COLUMN statut TEXT NOT NULL DEFAULT 'en_cours'
    CHECK (statut IN ('en_cours', 'terminee'));
ALTER TABLE sd_sessions ADD COLUMN elapsed_s INTEGER NOT NULL DEFAULT 0;
ALTER TABLE sd_sessions ADD COLUMN ended_at TEXT;
ALTER TABLE sd_sessions ADD COLUMN summary TEXT NOT NULL DEFAULT '';
ALTER TABLE sd_sessions ADD COLUMN summary_upto INTEGER NOT NULL DEFAULT 0;

ALTER TABLE sd_scenes ADD COLUMN content_hash TEXT NOT NULL DEFAULT '';

CREATE INDEX idx_sd_cases_type ON sd_cases(type);
CREATE INDEX idx_sd_sessions_case ON sd_sessions(case_id);
