"""Contenu du thème Transformers (texte original, à dire à l'oral)."""

from api.course_models import CardContent, Diagram, DiagramEdge, DiagramNode, ThemeContent
from api.seed.helpers import flow

SOURCE = "The Illustrated Transformer (Jay Alammar)"
PAPER = "Vaswani et al., 2017, « Attention Is All You Need »"


THEME = ThemeContent(
    slug="transformers",
    titre="Transformers",
    source_label=SOURCE,
    source_url="https://jalammar.github.io/illustrated-transformer/",
    cards=[
        CardContent(
            titre="Pourquoi le Transformer ?",
            accroche=(
                "Le Transformer remplace la récurrence par l'attention, ce qui permet de "
                "traiter tous les mots d'une phrase en parallèle."
            ),
            points=[
                "Avant 2017, on utilisait des RNN et des LSTM : ils lisent le texte mot par mot, "
                "donc impossible de paralléliser l'entraînement sur une séquence.",
                "Autre limite des RNN : l'information du début de la phrase s'efface "
                "avec la distance, les dépendances longues sont mal apprises.",
                "Le papier « Attention Is All You Need » (Google, 2017) propose une "
                "architecture sans récurrence, uniquement basée sur l'attention.",
                "Résultat : un entraînement très parallélisable sur GPU, donc des modèles "
                "qu'on a pu passer à l'échelle de milliards de paramètres.",
            ],
            source_label=PAPER,
            diagram=flow(["Texte", "Embeddings + positions", "Blocs d'attention", "Prédiction"]),
        ),
        CardContent(
            titre="Tokenisation",
            accroche=(
                "Le modèle ne lit pas des mots mais des tokens : des morceaux de mots "
                "choisis pour couvrir toute langue avec un vocabulaire de taille fixe."
            ),
            points=[
                "On utilise le plus souvent du BPE : on part des caractères et on fusionne "
                "les paires les plus fréquentes jusqu'à atteindre la taille de vocabulaire voulue.",
                "Les vocabulaires font typiquement entre 32 000 et plus de 128 000 tokens ; "
                "un mot rare est découpé en plusieurs sous-mots, un mot courant reste entier.",
                "Ordre de grandeur à citer : environ 3 à 4 caractères par token en anglais ; "
                "le français et le code consomment un peu plus de tokens pour le même texte.",
                "Cela compte pour le coût et la latence : on paie et on remplit la fenêtre "
                "de contexte en tokens, pas en mots.",
                "Les erreurs étranges sur les chiffres, l'orthographe ou les anagrammes "
                "viennent souvent de là : le modèle ne voit pas les lettres.",
            ],
            source_label=SOURCE,
            diagram=flow(["Texte brut", "Découpe BPE", "Identifiants", "Embeddings"]),
        ),
        CardContent(
            titre="Embeddings et encodage positionnel",
            accroche=(
                "Chaque token devient un vecteur, auquel on ajoute une information de position, "
                "car l'attention seule ne connaît pas l'ordre des mots."
            ),
            points=[
                "Un embedding est un vecteur appris par token ; dans le papier original, "
                "sa dimension est 512 (on parle de d_model).",
                "L'attention traite les tokens comme un ensemble : si on mélange l'ordre, "
                "le résultat est le même. Il faut donc injecter la position.",
                "Version d'origine : des sinusoïdes de fréquences différentes, ajoutées "
                "aux embeddings. Elles permettent de généraliser un peu à des longueurs inédites.",
                "Aujourd'hui, la plupart des LLM utilisent RoPE (rotary embeddings) : "
                "on fait tourner les vecteurs de requête et de clé selon leur position, "
                "ce qui encode une distance relative.",
            ],
            source_label=SOURCE,
            diagram=flow(["Token", "Embedding", "+ position", "Entrée du bloc"]),
        ),
        CardContent(
            titre="Self-attention",
            essentielle=True,
            accroche=(
                "Pour chaque token, la self-attention calcule une moyenne pondérée de "
                "tous les autres tokens, avec des poids qui dépendent du contenu."
            ),
            points=[
                "Chaque token produit trois vecteurs par projections apprises : "
                "une requête Q (ce que je cherche), une clé K (ce que je propose), "
                "une valeur V (ce que j'apporte).",
                "On compare Q et K par produit scalaire, on divise par racine de d_k, "
                "puis softmax : cela donne des poids qui somment à 1.",
                "La sortie est la somme des valeurs V pondérée par ces poids. "
                "Formule à dire : softmax(Q·Kᵀ / √d_k) · V.",
                "La division par √d_k évite que les produits scalaires deviennent grands "
                "et saturent le softmax, ce qui tuerait les gradients.",
                "Exemple oral : dans « la banque a fermé car elle était vide », "
                "« elle » doit pondérer fortement « banque ».",
            ],
            source_label=SOURCE,
            diagram=Diagram(
                nodes=[
                    DiagramNode(id="x", label="Entrée X", col=0, row=1),
                    DiagramNode(id="q", label="Q", col=1, row=0),
                    DiagramNode(id="k", label="K", col=1, row=1),
                    DiagramNode(id="v", label="V", col=1, row=2),
                    DiagramNode(id="s", label="Softmax(QKᵀ/√d)", col=2, row=0),
                    DiagramNode(id="o", label="Sortie", col=3, row=1),
                ],
                edges=[
                    DiagramEdge(source="x", target="q"),
                    DiagramEdge(source="x", target="k"),
                    DiagramEdge(source="x", target="v"),
                    DiagramEdge(source="q", target="s"),
                    DiagramEdge(source="k", target="s"),
                    DiagramEdge(source="s", target="o", label="poids"),
                    DiagramEdge(source="v", target="o"),
                ],
            ),
        ),
        CardContent(
            titre="Attention multi-têtes",
            essentielle=True,
            accroche=(
                "Au lieu d'une seule attention, on en lance plusieurs en parallèle sur des "
                "sous-espaces plus petits, pour capter plusieurs types de relations."
            ),
            points=[
                "Dans le papier : 8 têtes, avec d_model = 512, donc chaque tête travaille "
                "en dimension 64. Le coût total reste proche d'une seule grosse attention.",
                "Chaque tête a ses propres projections Q, K, V : l'une peut suivre la "
                "syntaxe, une autre les coréférences, une autre la proximité.",
                "On concatène les sorties de toutes les têtes, puis une projection de "
                "sortie W_O ramène à la dimension du modèle.",
                "Variantes à connaître pour l'inférence : multi-query et grouped-query "
                "attention partagent les clés et valeurs entre têtes pour réduire le KV cache.",
            ],
            source_label=SOURCE,
            diagram=Diagram(
                nodes=[
                    DiagramNode(id="x", label="Entrée", col=0, row=1),
                    DiagramNode(id="h1", label="Tête 1", col=1, row=0),
                    DiagramNode(id="h2", label="Tête 2", col=1, row=1),
                    DiagramNode(id="h3", label="Tête N", col=1, row=2),
                    DiagramNode(id="c", label="Concat + W_O", col=2, row=1),
                ],
                edges=[
                    DiagramEdge(source="x", target="h1"),
                    DiagramEdge(source="x", target="h2"),
                    DiagramEdge(source="x", target="h3"),
                    DiagramEdge(source="h1", target="c"),
                    DiagramEdge(source="h2", target="c"),
                    DiagramEdge(source="h3", target="c"),
                ],
            ),
        ),
        CardContent(
            titre="Feed-forward, résidus et normalisation",
            accroche=(
                "Autour de l'attention, chaque bloc ajoute un petit réseau dense appliqué "
                "token par token, des connexions résiduelles et une normalisation."
            ),
            points=[
                "Le feed-forward est un MLP à deux couches appliqué indépendamment à "
                "chaque position ; dans le papier : 512 vers 2048 puis retour à 512.",
                "C'est là que se trouve la majorité des paramètres d'un bloc : environ "
                "deux tiers, contre un tiers pour l'attention.",
                "La connexion résiduelle ajoute l'entrée à la sortie de chaque sous-couche : "
                "elle facilite la propagation du gradient dans des réseaux très profonds.",
                "LayerNorm stabilise l'entraînement. Les LLM récents normalisent avant la "
                "sous-couche (pre-norm), souvent avec RMSNorm, plus simple et plus rapide.",
            ],
            source_label=SOURCE,
            diagram=flow(["Entrée", "Attention", "Add & Norm", "Feed-forward", "Add & Norm"]),
        ),
        CardContent(
            titre="Masque causal et génération autorégressive",
            essentielle=True,
            accroche=(
                "Un modèle de langage génère un token à la fois, et le masque causal "
                "l'empêche de regarder les tokens futurs pendant l'entraînement."
            ),
            points=[
                "Le masque met à moins l'infini les scores vers les positions futures "
                "avant le softmax : la matrice d'attention devient triangulaire.",
                "Grâce à lui, on entraîne sur toute la séquence d'un coup (teacher forcing) "
                "tout en simulant la génération token par token.",
                "À l'inférence, on boucle : prédire la distribution du prochain token, "
                "échantillonner, ajouter le token à l'entrée, recommencer.",
                "L'échantillonnage se règle avec la température et top-p : température basse "
                "pour des sorties stables, plus haute pour de la diversité.",
                "Cette boucle séquentielle est la raison d'être du KV cache : on évite de "
                "recalculer les clés et valeurs des tokens déjà vus.",
            ],
            source_label=SOURCE,
            diagram=Diagram(
                nodes=[
                    DiagramNode(id="p", label="Prompt + tokens générés", col=0, row=0),
                    DiagramNode(id="m", label="Modèle", col=1, row=0),
                    DiagramNode(id="d", label="Distribution", col=2, row=0),
                    DiagramNode(id="t", label="Nouveau token", col=3, row=0),
                ],
                edges=[
                    DiagramEdge(source="p", target="m"),
                    DiagramEdge(source="m", target="d"),
                    DiagramEdge(source="d", target="t", label="sampling"),
                    DiagramEdge(source="t", target="p", label="boucle"),
                ],
            ),
        ),
        CardContent(
            titre="Encodeur, décodeur et cross-attention",
            accroche=(
                "Le Transformer d'origine a deux piles : un encodeur qui comprend l'entrée "
                "et un décodeur qui génère la sortie en s'appuyant sur elle."
            ),
            points=[
                "L'encodeur empile des blocs de self-attention bidirectionnelle : chaque "
                "token voit toute la phrase. Dans le papier : 6 blocs.",
                "Le décodeur empile aussi 6 blocs, avec une self-attention masquée "
                "puis une cross-attention vers la sortie de l'encodeur.",
                "Dans la cross-attention, les requêtes viennent du décodeur, les clés et "
                "valeurs de l'encodeur : c'est ainsi que la traduction « regarde » la source.",
                "Trois familles à citer : encodeur seul (BERT, pour classer ou embedder), "
                "décodeur seul (GPT, Mistral, Llama), encodeur-décodeur (T5).",
                "Aujourd'hui les LLM généralistes sont quasi tous décodeur seul : "
                "plus simple à passer à l'échelle et à entraîner sur du texte brut.",
            ],
            source_label=PAPER,
            diagram=Diagram(
                nodes=[
                    DiagramNode(id="i", label="Entrée", col=0, row=0),
                    DiagramNode(id="e", label="Encodeur (6 blocs)", col=1, row=0),
                    DiagramNode(id="d", label="Décodeur (6 blocs)", col=2, row=0),
                    DiagramNode(id="o", label="Sortie", col=3, row=0),
                ],
                edges=[
                    DiagramEdge(source="i", target="e"),
                    DiagramEdge(source="e", target="d", label="cross-attn"),
                    DiagramEdge(source="d", target="o"),
                ],
            ),
        ),
        CardContent(
            titre="Complexité et fenêtre de contexte",
            essentielle=True,
            accroche=(
                "L'attention compare chaque token à tous les autres : son coût grandit "
                "avec le carré de la longueur, ce qui limite la fenêtre de contexte."
            ),
            points=[
                "Pour n tokens, la matrice d'attention fait n par n : temps et mémoire en "
                "O(n²). Doubler le contexte multiplie ce terme par quatre.",
                "Les feed-forward, eux, sont linéaires en n ; sur de longs contextes, "
                "c'est l'attention qui domine.",
                "FlashAttention ne change pas le résultat mais calcule par blocs en "
                "mémoire rapide du GPU, ce qui évite de matérialiser la matrice complète.",
                "Autres leviers : l'attention à fenêtre glissante (utilisée dans Mistral 7B) "
                "et le grouped-query attention pour alléger le KV cache.",
                "Message d'entretien : un contexte long n'est pas gratuit, il coûte en "
                "latence, en mémoire GPU et souvent en qualité (information « perdue au milieu »).",
            ],
            source_label=PAPER,
            diagram=flow(["Contexte n", "Matrice n × n", "Mémoire et calcul en n²"]),
        ),
        CardContent(
            titre="Entraînement : prédire le token suivant",
            accroche=(
                "Un LLM de type décodeur est entraîné avec un objectif très simple : "
                "prédire le token suivant, sur des quantités énormes de texte."
            ),
            points=[
                "La perte est une entropie croisée entre la distribution prédite et le "
                "vrai token suivant, calculée à chaque position de la séquence.",
                "Ce pré-entraînement donne un modèle qui complète du texte, pas encore "
                "un assistant : on ajoute ensuite le fine-tuning sur instructions.",
                "Puis un alignement avec des préférences humaines (RLHF, DPO) pour que le "
                "modèle suive les consignes et refuse ce qui doit l'être.",
                "Les lois d'échelle relient performance, taille du modèle, quantité de "
                "données et calcul : pour un budget donné, il existe un équilibre à viser.",
            ],
            source_label=SOURCE,
            diagram=flow(
                ["Pré-entraînement", "Fine-tuning instructions", "Alignement", "Modèle chat"]
            ),
        ),
    ],
)
