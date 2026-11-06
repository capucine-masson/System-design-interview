# Prépa System Design

Application web locale (un seul utilisateur) pour s'entraîner aux entretiens de system design :
cours en cartes, entretien manager à l'oral, System Design avec Excalidraw. Tout est sauvegardé en SQLite.

> État : étape 4. Cours (13 thèmes, dont Python, outils dev et CI/CD/infra, sans IA), Entretien manager et System Design (brief, interviewer, Excalidraw) fonctionnent ; IA sur clic uniquement. La correction du System Design est incluse.

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

Ouvrir `http://localhost:<FRONT_PORT>`. La base est créée et migrée au démarrage du backend (la migration `006_lang.sql` ajoute la langue aux cas et questions déjà en base, en français).

## Contenu du cours

Le contenu (thèmes, cartes, schémas) est écrit dans `api/seed/` (français) et `api/seed/en/` (anglais), et inséré en base par un script, sans réseau ni IA.
Relançable sans risque : la progression (maîtrisée / à revoir) est conservée.

```powershell
uv run python -m api.seed
```

## Révision des cartes

**Révision aléatoire** (page Cours) tire des cartes de tous les thèmes ; **Réviser ce thème** se limite à ce thème.

1. Choisir le nombre de cartes (5, 10 ou max) et, au besoin, « seulement à revoir ».
2. Pour chaque carte, expliquer la notion à l'oral (**Dicter ma réponse**) ou au clavier, puis **Envoyer pour correction**.
3. L'IA (1 appel par carte, visible dans **Consommation**) dit ce qui est juste, ce qui manque, les erreurs, et explique simplement ce qu'il fallait dire.
4. Marquer la carte « maîtrisée » ou « à revoir » toi-même, puis passer à la suivante.

La dictée suit les mêmes règles que l'entretien manager (Chrome ou Edge ; sinon, tape ta réponse).

## Mistral Workflows

Section à part, sur le modèle des Cours, pour s'entraîner à expliquer **Mistral Workflows** (orchestration durable de Mistral Studio). 12 catégories (positionnement, déterminisme, retries, agents, déploiement, sécurité, mises en situation FDE…) et leurs cartes, avec progression « maîtrisée / à revoir » et révision corrigée par l'IA.

- Contenu écrit en français dans `api/seed/workflows/` (un fichier par catégorie), chaque carte pointe vers la page de la doc officielle. Chargé par la même commande `uv run python -m api.seed` (relançable sans risque).
- Tables et routes séparées des Cours (`wf_*`, `/api/workflows/...`) : la progression des deux sections est indépendante.
- Les cartes restent en français quand l'interface est en anglais ; seuls les libellés de la section sont traduits.
- Ce que la doc ne documente pas (valeurs par défaut des retries, versioning, Helm chart) est signalé comme tel dans les cartes : ne pas l'affirmer.

## Entretien manager

1. Choisir une catégorie et une difficulté, puis **Générer une question** (1 appel IA, rangée dans la banque) ou **Tirer de la banque** (gratuit).
2. Répondre à l'oral (**Dicter ma réponse**) ou au clavier ; le texte reste modifiable. Chrono avec objectif de 2 à 3 minutes.
3. Le manager pose une relance (1 appel IA) ; au plus 3 réponses par question.
4. **Terminer et obtenir le retour** (1 appel IA) : notes, points forts et faibles, oublis, réponse améliorée, 2 conseils.
5. Les sessions et l'évolution des notes sont dans **Historique**.

Un cycle complet coûte 3 à 5 appels IA, tous visibles dans **Consommation**.

La dictée vocale utilise le navigateur (gratuit, dans la langue choisie, internet requis). Utilise **Chrome** ou **Edge** sur ordinateur ; Firefox ne la propose pas. Sinon, tape ta réponse.

Le retour structuré est long : garde `LLM_MAX_TOKENS` à 1500 ou plus.

## System Design

1. Choisir un cas (ou « Au hasard »), puis **Générer un brief** (1 appel IA, rangé dans la banque) ou **Tirer de la banque** (gratuit).
2. Le brief est volontairement flou : les chiffres (volumétrie, latence, budget...) sont cachés côté serveur et ne sont révélés que si tu poses la bonne question à l'interviewer.
3. Discuter par écrit ou à l'oral (**Dicter**, Chrome ou Edge) ; chaque message envoyé = 1 appel IA. Le contexte envoyé reste court (derniers messages + résumé glissant). 40 messages maximum par session.
4. Dessiner dans Excalidraw (raccourcis R, A, T, D, Ctrl+D... actifs quand le canvas a le focus). Le panneau **Bibliothèque** contient un cylindre « base de données », une file, un service externe et un utilisateur. Le schéma est sauvegardé automatiquement (versions horodatées, bouton **Versions** pour revenir en arrière).
5. Minuteur de 45 minutes avec les étapes conseillées (indicatif, il ne bloque rien). **Terminer et obtenir la correction** clôt la session puis génère la correction (jusqu'à 2 appels IA : la solution de référence du cas, générée une seule fois et réutilisée, puis ta correction). Tu y vois tes notes par étape, les détails que l'interviewer te cachait (obtenus ou non), les composants manquants, et la solution de référence avec son schéma. Une session déjà terminée propose le bouton **Obtenir la correction détaillée**.
6. Rouvre une session depuis **System Design** ou **Historique** : brief, chat, schéma et temps sont restaurés.

Cas disponibles : 9 systèmes ML/LLM (RAG, inférence, entraînement, évaluation, agent, recommandation, serving d'un MoE avec cible p95, API LLM multi-tenant avec quotas en tokens et paliers de SLA, fine-tuning et serving multi-adaptateurs LoRA) et 19 cas classiques (Google Docs, streaming vidéo, raccourcisseur d'URL, messagerie, fil d'actualité, VTC, stockage de fichiers, limiteur de débit, notifications, autocomplétion, crawler, paiement, billetterie, base clé-valeur, sessions utilisateur, permissions, commandes en ligne avec panier, bibliothèque, blog), dont plusieurs inspirés de [cette liste de questions](https://www.finalroundai.com/blog/system-design-interview-questions).

Ajouter un type de cas : ajouter une entrée dans `api/sd_catalog.py` avec sa `famille` (`ml` ou `classique`), et sa version anglaise (même `slug`) dans `api/sd_catalog_en.py`.

Les prompts (`api/llm.py`) font couvrir à chaque cas, à l'interviewer, à la solution de référence et à la correction quatre dimensions : stockage de données, architecture, répartition de charge et optimisation de performance ; les cas ML/LLM ajoutent des détails propres aux LLM (mémoire GPU, tokens par seconde, p95, paliers de clients). Les cas déjà en banque gardent leurs anciens détails.

`api/scene_text.py` transforme ton schéma Excalidraw en description texte (composants, étiquettes, flèches) envoyée au modèle pour la correction, sans image.

Les polices d'Excalidraw sont chargées depuis un CDN : internet est requis (comme pour Mistral et la dictée).

## Langue (français / anglais)

Les drapeaux en haut à droite basculent **toute l'application** : interface, catalogue des cas, messages d'erreur, et réponses de l'IA (brief, interviewer, relances, retours, corrections). Le choix est mémorisé dans le navigateur.

- Le frontend envoie la langue dans l'en-tête `X-Lang` ; le backend la lit dans `api/lang.py`.
- Chaque cas System Design et chaque question manager est stocké avec sa langue : la banque (**Tirer de la banque**) ne propose que les éléments de la langue choisie. Les éléments déjà générés restent en français ; en anglais, il faut d'abord **Générer** (1 appel IA).
- Une session garde la langue de son cas, même si tu changes de drapeau en cours de route.
- Les cours sont aussi traduits : le français est dans `api/seed/*.py`, l'anglais dans `api/seed/en/*.py` (mêmes cartes, même ordre ; pour les schémas, seuls les libellés sont traduits). Relance `uv run python -m api.seed` pour charger les traductions. La progression (maîtrisée / à revoir) est commune aux deux langues. Une carte sans traduction s'affiche en français.
- Ajouter un texte d'interface : une clé dans `web/src/locales/fr.ts` et la même dans `web/src/locales/en.ts` (le build échoue s'il en manque une).

## Variables `.env`

Toutes sont requises : le backend refuse de démarrer si l'une est vide.

> Après avoir modifié `.env`, recharge-le dans le shell (la commande de la section Lancement) puis **redémarre le backend** : les variables déjà définies dans le shell ne sont pas écrasées, donc l'ancienne valeur reste active sinon.

| Variable | Rôle |
| --- | --- |
| `API_PORT` / `FRONT_PORT` | Ports du backend et du frontend (origine CORS et URL de l'API en sont déduites) |
| `DB_PATH` | Fichier SQLite (relatif à la racine du projet) |
| `MISTRAL_API_KEY` | Clé API du fournisseur IA (reste côté serveur) |
| `MISTRAL_MODEL` | ID exact du modèle |
| `MISTRAL_PRICE_INPUT_PER_M` / `MISTRAL_PRICE_OUTPUT_PER_M` | Prix par million de tokens (entrée / sortie), pour le coût estimé |
| `LLM_MAX_TOKENS` | Plafond de tokens générés par appel (2500 conseillé : la solution de référence est longue) |
| `LLM_TIMEOUT_S` | Délai maximum d'un appel IA, en secondes (90 conseillé) |

## Vérifications

```powershell
uv run ruff check .
uv run mypy .
uv run pytest        # n'appelle jamais le vrai modèle (faux client)
cd web; pnpm test; pnpm build
```
