-- Coche manuelle « thème maîtrisé », indépendante de la progression des cartes
ALTER TABLE themes ADD COLUMN fait INTEGER NOT NULL DEFAULT 0;
ALTER TABLE wf_themes ADD COLUMN fait INTEGER NOT NULL DEFAULT 0;
