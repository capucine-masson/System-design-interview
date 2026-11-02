-- Cours
CREATE TABLE themes (
    id INTEGER PRIMARY KEY,
    titre TEXT NOT NULL,
    ordre INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE cards (
    id INTEGER PRIMARY KEY,
    theme_id INTEGER NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    titre TEXT NOT NULL,
    explication_orale TEXT NOT NULL,
    schema TEXT,
    source_url TEXT,
    ordre INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE card_progress (
    card_id INTEGER PRIMARY KEY REFERENCES cards(id) ON DELETE CASCADE,
    statut TEXT NOT NULL CHECK (statut IN ('maitrisee', 'a_revoir')),
    updated_at TEXT NOT NULL
);

-- Entretien manager
CREATE TABLE manager_questions (
    id INTEGER PRIMARY KEY,
    categorie TEXT NOT NULL,
    contexte TEXT NOT NULL,
    enonce TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE manager_sessions (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL
);
CREATE TABLE manager_answers (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES manager_sessions(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES manager_questions(id),
    transcription TEXT NOT NULL,
    duree_s INTEGER,
    created_at TEXT NOT NULL
);
CREATE TABLE manager_feedbacks (
    id INTEGER PRIMARY KEY,
    answer_id INTEGER NOT NULL UNIQUE REFERENCES manager_answers(id) ON DELETE CASCADE,
    feedback_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- System design
CREATE TABLE sd_cases (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    brief TEXT NOT NULL,
    params_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE TABLE sd_sessions (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES sd_cases(id),
    created_at TEXT NOT NULL
);
CREATE TABLE sd_messages (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sd_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE sd_scenes (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sd_sessions(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    scene_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (session_id, version)
);
CREATE TABLE sd_corrections (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL UNIQUE REFERENCES sd_sessions(id) ON DELETE CASCADE,
    correction_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE sd_references (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL UNIQUE REFERENCES sd_cases(id) ON DELETE CASCADE,
    contenu TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Journal des appels IA
CREATE TABLE llm_calls (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    feature TEXT NOT NULL,
    model TEXT NOT NULL,
    tokens_in INTEGER NOT NULL,
    tokens_out INTEGER NOT NULL,
    cost_estimate REAL NOT NULL
);

CREATE INDEX idx_cards_theme ON cards(theme_id, ordre);
CREATE INDEX idx_manager_answers_session ON manager_answers(session_id);
CREATE INDEX idx_sd_messages_session ON sd_messages(session_id, id);
CREATE INDEX idx_llm_calls_feature ON llm_calls(feature);
