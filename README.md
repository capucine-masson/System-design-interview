# Prépa Mistral

Application web locale (un seul utilisateur) pour préparer un entretien MLE / LLM chez Mistral AI :
cours en cartes, entretien manager à l'oral, System Design avec Excalidraw. Tout est sauvegardé en SQLite.

> État : étape 2. Section Cours (cartes, progression, révision aléatoire) fonctionnelle, sans IA. Seul le thème Transformers est rédigé pour l'instant. Aucune génération IA n'est encore branchée.

## Installation

Prérequis : Python 3.12+, [uv](https://docs.astral.sh/uv/), Node et pnpm.

```powershell
Copy-Item .env.example .env   # puis remplir .env (voir ci-dessous)
uv sync
cd web; pnpm install; cd ..
```

## Lancement

Backend (charge le `.env` dans le shell pour lire `API_PORT`) :

```powershell
Get-Content .env | ForEach-Object { $k,$v = $_ -split '=',2; if ($k -and $k -notmatch '^#') { Set-Item "env:$k" $v } }
uv run uvicorn api.main:app --reload --port $env:API_PORT
```

Frontend (autre terminal) :

```powershell
cd web
pnpm dev
```

Ouvrir `http://localhost:<FRONT_PORT>`. La base est créée et migrée au démarrage du backend.

## Contenu du cours

Le contenu (thèmes, cartes, schémas) est écrit dans `api/seed/` et inséré en base par un script, sans réseau ni IA.
Relançable sans risque : la progression (maîtrisée / à revoir) est conservée.

```powershell
uv run python -m api.seed
```

## Variables `.env`

Toutes sont requises : le backend refuse de démarrer si l'une est vide.

| Variable | Rôle |
| --- | --- |
| `API_PORT` / `FRONT_PORT` | Ports du backend et du frontend (origine CORS et URL de l'API en sont déduites) |
| `DB_PATH` | Fichier SQLite (relatif à la racine du projet) |
| `MISTRAL_API_KEY` | Clé API Mistral (reste côté serveur) |
| `MISTRAL_MODEL` | ID exact du modèle, ex. `mistral-small-2603` |
| `MISTRAL_PRICE_INPUT_PER_M` / `MISTRAL_PRICE_OUTPUT_PER_M` | Prix par million de tokens (entrée / sortie), pour le coût estimé |
| `LLM_MAX_TOKENS` | Plafond de tokens générés par appel |
| `LLM_TIMEOUT_S` | Délai maximum d'un appel IA, en secondes |

## Vérifications

```powershell
uv run ruff check .
uv run mypy .
uv run pytest        # n'appelle jamais le vrai modèle (faux client)
cd web; pnpm test; pnpm build
```
