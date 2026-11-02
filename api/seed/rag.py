"""Contenu du thème RAG et recherche (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

RAG_PAPER = (
    "Lewis et al., 2020, « Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks »"
)
RAG_URL = "https://arxiv.org/abs/2005.11401"
SBERT = "Reimers et Gurevych, 2019, « Sentence-BERT »"
SBERT_URL = "https://arxiv.org/abs/1908.10084"
DPR = "Karpukhin et al., 2020, « Dense Passage Retrieval »"
DPR_URL = "https://arxiv.org/abs/2004.04906"
HNSW = "Malkov et Yashunin, « Hierarchical Navigable Small World graphs »"
HNSW_URL = "https://arxiv.org/abs/1603.09320"
CHUNKING = "Pinecone, « Chunking Strategies for LLM Applications »"
CHUNKING_URL = "https://www.pinecone.io/learn/chunking-strategies"
RERANK = "Nogueira et Cho, 2019, « Passage Re-ranking with BERT »"
RERANK_URL = "https://arxiv.org/abs/1901.04085"
EVALS = "AI Evals FAQ (Hamel Husain)"
EVALS_URL = "https://hamel.dev/blog/posts/evals-faq/"

THEME = ThemeContent(
    slug="rag",
    titre="RAG et recherche",
    source_label="Articles et guides publics, cités carte par carte",
    source_url=None,
    cards=[
        CardContent(
            titre="Pourquoi le RAG",
            accroche=(
                "Le RAG donne au modèle les bons documents au moment de répondre, "
                "au lieu de compter sur sa mémoire."
            ),
            points=[
                "Problèmes visés : connaissances périmées, données privées que le "
                "modèle n'a jamais vues, hallucinations sur des faits précis.",
                "Principe : retrouver des passages pertinents, les insérer dans le "
                "prompt, générer une réponse appuyée sur eux, avec citations possibles.",
                "Mettre à jour la base de documents suffit, sans réentraîner le modèle.",
                "RAG ou fine-tuning ? Le RAG apporte des faits, le fine-tuning "
                "apporte un style ou un comportement ; on les combine parfois.",
            ],
            source_label=RAG_PAPER,
            source_url=RAG_URL,
            diagram=flow(["Question", "Recherche", "Passages", "LLM", "Réponse citée"]),
        ),
        CardContent(
            titre="Embeddings",
            accroche=(
                "Un embedding transforme un texte en vecteur, de sorte que des "
                "textes de sens proche donnent des vecteurs proches."
            ),
            points=[
                "Un bi-encodeur encode séparément la question et chaque document ; "
                "on compare ensuite par similarité cosinus ou produit scalaire.",
                "Les documents sont encodés une fois à l'avance ; seule la "
                "question est encodée à la requête, d'où la rapidité.",
                "Dimensions typiques : de quelques centaines à environ 3 000 ; plus "
                "grand veut dire plus de mémoire et de temps de recherche.",
                "Choisir selon la langue (multilingue pour le français), le domaine, "
                "la longueur maximale d'entrée et le coût ; puis mesurer sur ses données.",
            ],
            source_label=SBERT,
            source_url=SBERT_URL,
        ),
        CardContent(
            titre="Chunking",
            accroche=(
                "Découper les documents en morceaux de bonne taille est souvent le "
                "réglage qui influence le plus la qualité du RAG."
            ),
            points=[
                "Trop gros : le passage dilue l'information et consomme du contexte ; "
                "trop petit : on perd le contexte nécessaire pour comprendre.",
                "Ordre de grandeur de départ : quelques centaines de tokens, avec "
                "un recouvrement de 10 à 20 % entre morceaux.",
                "Mieux vaut découper selon la structure (titres, paragraphes, "
                "fonctions de code) que par taille fixe aveugle.",
                "Stocker des métadonnées (titre, section, date, source) pour filtrer et pour "
                "citer.",
                "On teste plusieurs tailles et on garde celle qui maximise le "
                "recall sur ses propres questions.",
            ],
            source_label=CHUNKING,
            source_url=CHUNKING_URL,
        ),
        CardContent(
            titre="Bases vectorielles et recherche approximative",
            accroche=(
                "Une base vectorielle retrouve rapidement les vecteurs les plus "
                "proches parmi des millions, en acceptant une approximation."
            ),
            points=[
                "La recherche exacte compare à tous les vecteurs : coût linéaire, "
                "trop lent à grande échelle.",
                "HNSW construit un graphe en couches : on descend de couche en "
                "couche en suivant les voisins les plus proches ; très bon compromis "
                "rappel/latence.",
                "Autres familles : index inversé par clusters (IVF) et compression "
                "des vecteurs (quantification par produit) pour économiser la mémoire.",
                "Réglages à citer : le rappel visé, la latence, la mémoire, et le "
                "filtrage par métadonnées combiné à la recherche.",
                "Pour quelques milliers de documents, une simple recherche exacte "
                "ou une extension de base de données suffit.",
            ],
            source_label=HNSW,
            source_url=HNSW_URL,
        ),
        CardContent(
            titre="Recherche dense",
            accroche=(
                "La recherche dense compare des sens plutôt que des mots : elle "
                "retrouve des passages même sans mot en commun."
            ),
            points=[
                "Un encodeur appris, entraîné sur des paires question-passage, "
                "place les bonnes paires proches dans l'espace vectoriel.",
                "Force : synonymes, paraphrases, questions en langage naturel.",
                "Faiblesse : termes rares, identifiants, noms propres, codes "
                "d'erreur, que la recherche lexicale retrouve mieux.",
                "Elle dépend du domaine d'entraînement : à tester sur ses propres "
                "documents avant de s'y fier.",
            ],
            source_label=DPR,
            source_url=DPR_URL,
        ),
        CardContent(
            titre="Recherche hybride",
            accroche=(
                "On combine la recherche lexicale (BM25) et la recherche dense "
                "pour couvrir à la fois les mots exacts et le sens."
            ),
            points=[
                "BM25 note les documents selon la fréquence des mots de la question, "
                "pondérée par leur rareté et la longueur du document.",
                "On lance les deux recherches en parallèle, puis on fusionne les "
                "listes, souvent par fusion de rangs (RRF), qui évite de comparer des scores de "
                "natures différentes.",
                "Cette combinaison est un bon réglage par défaut pour des "
                "documents mêlant prose et termes techniques.",
                "Coût : deux index à maintenir et une étape de fusion de plus.",
            ],
            source_label="Robertson et Zaragoza, 2009, « The Probabilistic Relevance Framework »",
            diagram=graph(
                [
                    ("q", "Question", 0, 1),
                    ("b", "BM25", 1, 0),
                    ("d", "Vecteurs", 1, 2),
                    ("f", "Fusion (RRF)", 2, 1),
                ],
                [("q", "b"), ("q", "d"), ("b", "f"), ("d", "f")],
            ),
        ),
        CardContent(
            titre="Reranking",
            accroche=(
                "On récupère large avec une recherche rapide, puis un modèle plus "
                "précis réordonne les meilleurs candidats."
            ),
            points=[
                "Un cross-encodeur lit la question et le passage ensemble : plus "
                "précis qu'un bi-encodeur, mais trop lent pour toute la base.",
                "Schéma courant : récupérer 50 à 100 candidats, réordonner, garder "
                "les 5 à 10 meilleurs pour le prompt.",
                "Gain typique sur la pertinence des premiers résultats, au prix "
                "d'une latence supplémentaire de quelques dizaines à centaines de ms.",
                "À ajouter quand les bons passages sont dans les candidats mais "
                "mal classés : on le voit avec le recall@k contre la précision@k.",
            ],
            source_label=RERANK,
            source_url=RERANK_URL,
            diagram=flow(["Question", "Top 100 rapide", "Reranker", "Top 5 au LLM"]),
        ),
        CardContent(
            titre="Construire le prompt de génération",
            accroche=(
                "Le prompt doit dire au modèle de s'appuyer sur les passages "
                "fournis et d'avouer quand ils ne suffisent pas."
            ),
            points=[
                "Délimiter clairement les passages (balises, numéros) et les "
                "présenter comme des données, pas comme des instructions.",
                "Demander de répondre uniquement à partir du contexte, de citer "
                "les passages utilisés, et de dire « je ne sais pas » sinon.",
                "Attention à la place de l'information : les modèles exploitent "
                "parfois mal les passages situés au milieu d'un long contexte.",
                "Limiter le nombre de passages : plus n'est pas toujours mieux, "
                "du bruit dégrade la réponse et coûte des tokens.",
                "Un document récupéré peut contenir des instructions "
                "malveillantes (injection de prompt) : ne jamais les exécuter.",
            ],
            source_label=RAG_PAPER,
            source_url=RAG_URL,
        ),
        CardContent(
            titre="Évaluer la recherche",
            accroche=(
                "On évalue d'abord la récupération seule : a-t-on trouvé les bons "
                "passages, et bien classés ?"
            ),
            points=[
                "On construit un jeu de questions avec les passages qui y répondent, "
                "à la main ou en générant des questions à partir des documents.",
                "Recall@k : la bonne réponse est-elle dans les k premiers ? "
                "C'est la métrique clé, car le LLM ne peut pas utiliser ce qu'il ne reçoit pas.",
                "MRR et nDCG ajoutent la position du bon passage dans le classement.",
                "Pour la recherche, ces métriques de rang sont adaptées, contrairement "
                "aux scores génériques sur du texte généré.",
            ],
            source_label=EVALS,
            source_url=EVALS_URL,
        ),
        CardContent(
            titre="Évaluer la génération et diagnostiquer",
            accroche=(
                "Une fois la recherche mesurée, on vérifie que la réponse est "
                "fidèle aux passages et répond à la question."
            ),
            points=[
                "Fidélité (groundedness) : chaque affirmation est-elle soutenue "
                "par les passages fournis ? Un juge LLM validé sur des étiquettes humaines peut "
                "s'en charger.",
                "Pertinence de la réponse : répond-elle réellement à la "
                "question posée, sans digresser ?",
                "Diagnostic : mauvais passage récupéré, bon passage ignoré, ou "
                "mauvaise génération ? Chaque cause a sa correction (recherche, prompt, modèle).",
                "On part de l'analyse d'erreurs sur de vraies traces avant "
                "de choisir les métriques.",
            ],
            source_label=EVALS,
            source_url=EVALS_URL,
        ),
        CardContent(
            titre="Améliorer un RAG qui déçoit",
            accroche=(
                "Quand le RAG répond mal, je cherche d'abord où il échoue, puis "
                "j'applique le levier correspondant."
            ),
            points=[
                "Réécriture de la requête : reformuler une question vague ou "
                "l'enrichir avec l'historique de conversation avant la recherche.",
                "Récupérer de petits morceaux précis mais fournir au modèle le "
                "paragraphe ou la section parente pour garder le contexte.",
                "Filtres de métadonnées (date, produit, droits d'accès) pour "
                "réduire le champ de recherche.",
                "Ajouter recherche hybride puis reranking si le recall est insuffisant.",
                "Les droits d'accès doivent s'appliquer à la recherche : un "
                "utilisateur ne doit pas lire via le RAG ce qu'il ne peut pas ouvrir.",
            ],
            source_label="Synthèse de pratiques courantes",
        ),
    ],
)
