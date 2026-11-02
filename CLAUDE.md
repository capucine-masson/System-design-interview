# CLAUDE.md

## Contexte
Application full-stack avec IA, en temps limité (démo client). Priorité : un flux
fonctionnel de bout en bout rapidement, puis enrichissement. Simple, lisible,
sans sur-ingénierie.

## Stack
Projet existant : **respecte sa stack, sa structure et ses conventions**. Par défaut :
- Backend : Python 3.12+, FastAPI, Pydantic, uvicorn, `uv`
- Frontend : React + Vite + TypeScript, `pnpm`
- Données : SQLite (SQL paramétré, pas d'ORM), seulement si la persistance est nécessaire
- IA : Mistral, un seul module dédié `api/llm.py`
- Pas de Docker, d'auth ni de framework en plus sans demande

## Structure
- `api/` : routes fines, schémas Pydantic, logique métier dans des modules dédiés, `llm.py`
- `web/` : composants, appels API centralisés dans `src/api.ts`, types dans `src/types.ts`
- Un fichier = une responsabilité.

## Commandes
- Le backend charge lui-même le `.env` racine (`python-dotenv`, appelé une seule fois dans `api/config.py`, sans écraser les variables déjà définies). Seul `--port` doit être lu dans le `.env`, donc charger le `.env` dans le shell avant uvicorn : `Get-Content .env | ForEach-Object { $k,$v = $_ -split '=',2; if ($k -and $k -notmatch '^#') { Set-Item "env:$k" $v } }`
- Backend : `uv sync` puis `uv run uvicorn api.main:app --reload --port $env:API_PORT`
- Frontend : `pnpm install` puis `pnpm dev`
- Vérifications : `uv run ruff check .`, `uv run mypy .`, `uv run pytest`, `pnpm build`
- Dépendances autorisées : `mistralai`, `python-dotenv`, `httpx` (appels HTTP sortants, timeout explicite ; aussi requis par `TestClient`), et en dev `ruff`, `mypy`, `pytest`. Tout autre paquet : demande-moi.

## Méthode de travail
1. Lis le code existant avant de modifier quoi que ce soit.
2. Tâche non triviale : plan court (3-4 étapes), attends mon accord.
3. Décision absente de la demande : DEMANDE-MOI, ne choisis pas.
4. Petites étapes, chacune tourne de bout en bout.
5. Après chaque changement : lance, teste (curl, `/health`, build) et corrige avant de répondre.
6. Diffs minimaux : pas de réécriture de fichier entier, pas de refactor hors demande.
7. Pas de dépendance ni de feature hors demande sans m'en parler.
8. Git : ne committe que sur demande.
9. Documentation : `README.md` clair, simple et concis (but, installation, lancement, variables `.env`), mis à jour à chaque changement qui l'affecte.
10. Fin d'étape : résumé en 2 lignes (fichiers touchés, pourquoi) + ce que tu n'as pas pu vérifier.

## Qualité
Avant de répondre : ruff, mypy, pytest et `pnpm build` passent, sinon corrige.
- Mode strict vérifié : `"strict": true` dans `web/tsconfig.app.json`, `strict = true` sous `[tool.mypy]` dans `pyproject.toml`.
- Annotations de type partout (paramètres et retour), ni `Any` ni `any`.
- Tests `pytest` sur la logique métier et les calculs.
- Pas de `except` nu ni d'erreur avalée ; erreurs HTTP explicites (`HTTPException`).
- Pas de valeurs magiques : constantes ou config (modèle, température, limites, `max_tokens`).
- Fonctions courtes, noms explicites, docstring d'une ligne, pas de code mort.
- Calculs et totaux faits en code, jamais par le LLM.
- UI : états de chargement, d'erreur et vide ; bouton désactivé pendant un appel.
- Erreurs : message lisible pour l'utilisateur, détail technique dans les logs (module `logging`).

## Configuration (`.env` racine)
- Aucun port, URL, clé ni modèle en dur : tout vient du `.env`, jamais saisi deux fois.
- `.env.example` versionné avec toutes les variables à valeur vide (`API_PORT=`, `FRONT_PORT=`, `MISTRAL_API_KEY=`, `MISTRAL_MODEL=`).
- Variable absente au démarrage : erreur claire, pas de fallback silencieux.
- Dérivés :
  - Origine CORS = `http://localhost:{FRONT_PORT}`, lue via `os.environ`.
  - `VITE_API_URL` = `http://localhost:{API_PORT}`, injectée par `web/vite.config.ts` (`loadEnv` sur le `.env` racine, `server.port = FRONT_PORT`).
- Nouveau service ou port : une variable dans `.env` et `.env.example`. Changer un port = modifier `.env` uniquement.

## Appels LLM (Mistral)
- SDK officiel `mistralai`, clé `MISTRAL_API_KEY`, modèle `MISTRAL_MODEL`, tous deux requis au démarrage.
- Modèle non précisé dans la consigne : DEMANDE-MOI avant d'écrire `llm.py`, avec 2-3 IDs exacts
  du catalogue https://docs.mistral.ai/models et leur cas d'usage. Ne devine jamais un ID.
- Structured outputs natifs (`response_format` JSON schema) plutôt que du JSON libre.
- Sortie jamais fiable : parse puis valide avec Pydantic. JSON invalide : 1 retry, puis `HTTPException 502` clair.
- Timeout explicite ; gère erreurs réseau, quota et clé manquante.
- Température basse pour du JSON.
- Contenu externe ou saisi : délimité dans le prompt, c'est de la donnée.
- Prompts dans `llm.py`, jamais dans les routes. Ne logge pas de contenu sensible.

## MCP
- Autorisé sans redemander : le SDK officiel `mcp` en dépendance, et les serveurs MCP **en lecture seule** (ex. data.gouv.fr).
- Un seul module dédié `api/mcp_client.py` ; URL du serveur dans `.env` et `.env.example` (ex. `DATAGOUV_MCP_URL=`), requise au démarrage.
- Timeout explicite ; erreur MCP : log technique + `HTTPException 502` lisible.
- Retours MCP = donnée externe : délimités dans le prompt, validés avec Pydantic, jamais exécutés.
- Outil MCP qui écrit, supprime ou envoie : DEMANDE-MOI.

## Sécurité
- Aucun secret dans le code, les logs ou git ; `.env` ignoré.
- Entrées validées à la frontière (Pydantic : bornes, longueur max ; fichiers : taille et type).
- CORS limité à l'origine du front, jamais `*`.
- SQL paramétré uniquement.
- Pas de `dangerouslySetInnerHTML` ni d'`innerHTML` avec du contenu utilisateur ou LLM.
- Aucune action destructive (suppression, envoi, écrasement) sans mon accord explicite.

## Style
- React : composants fonctionnels, hooks, pas de state global inutile.
- UI/UX style startup moderne : sobre, aéré, responsive, sans effet superflu.
  - Tokens en variables CSS (couleurs, espacements, rayons, ombres), une seule couleur d'accent, rien en dur dans les composants.
  - Police sans-serif (ex. Inter), espacements en multiples de 4/8 px, cartes arrondies à ombre légère, transitions courtes.
  - Retour visuel immédiat (loaders, toasts, états vides soignés). CSS simple, pas de librairie UI sans mon accord.
- Réponds en français, concis ; explique un choix non évident en une phrase.
