-- Entretien manager : scénario complet, lien session -> question, relances de l'IA
ALTER TABLE manager_questions ADD COLUMN difficulte TEXT NOT NULL DEFAULT 'moyenne';
ALTER TABLE manager_questions ADD COLUMN contraintes_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE manager_questions ADD COLUMN enjeu TEXT NOT NULL DEFAULT '';

ALTER TABLE manager_sessions ADD COLUMN question_id INTEGER REFERENCES manager_questions(id);
ALTER TABLE manager_sessions ADD COLUMN statut TEXT NOT NULL DEFAULT 'en_cours'
    CHECK (statut IN ('en_cours', 'terminee'));

CREATE TABLE manager_followups (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES manager_sessions(id) ON DELETE CASCADE,
    answer_id INTEGER NOT NULL UNIQUE REFERENCES manager_answers(id) ON DELETE CASCADE,
    texte TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_manager_sessions_question ON manager_sessions(question_id);
CREATE INDEX idx_manager_questions_filter ON manager_questions(categorie, difficulte);
