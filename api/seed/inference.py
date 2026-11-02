"""Contenu du thème Optimisation de l'inférence (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

SOURCE = "Large Transformer Model Inference Optimization (Lilian Weng, 2023)"

THEME = ThemeContent(
    slug="inference",
    titre="Optimisation de l'inférence",
    source_label=SOURCE,
    source_url="https://lilianweng.github.io/posts/2023-01-10-inference-optimization/",
    cards=[
        CardContent(
            titre="Prefill et decode : deux régimes",
            accroche=(
                "Servir un LLM, c'est deux phases très différentes : lire le prompt "
                "d'un coup, puis générer la réponse token par token."
            ),
            points=[
                "Le prefill traite tout le prompt en parallèle : beaucoup de calcul, "
                "le GPU est limité par sa puissance de calcul (compute-bound).",
                "Le decode produit un token à la fois : chaque étape relit tous les "
                "poids et le KV cache, donc on est limité par la bande passante mémoire.",
                "Trois métriques à citer : le TTFT (délai avant le premier token), "
                "le temps par token généré, et le débit global en tokens par seconde.",
                "Presque toutes les optimisations visent l'un des deux régimes : "
                "réduire les octets lus au decode, ou mieux remplir le GPU.",
            ],
            source_label=SOURCE,
            diagram=flow(["Prompt", "Prefill (parallèle)", "Decode (token à token)", "Réponse"]),
        ),
        CardContent(
            titre="KV cache",
            accroche=(
                "Le KV cache garde les clés et valeurs déjà calculées pour ne pas "
                "refaire l'attention sur tout le passé à chaque nouveau token."
            ),
            points=[
                "Sans cache, chaque token généré recalculerait K et V de tout le "
                "contexte ; avec, on ne calcule que le nouveau token et on lit le reste.",
                "Taille approximative : 2 (K et V) × couches × têtes KV × dimension "
                "de tête × octets × tokens × taille de batch.",
                "Exemple à citer : un modèle 7B classique en fp16 (32 couches, "
                "4096 de dimension) coûte environ 0,5 Mo par token, soit ~2 Go pour "
                "4 000 tokens et par requête.",
                "Conséquence : le cache, pas les poids, limite souvent le nombre de "
                "requêtes simultanées sur un GPU.",
            ],
            source_label=SOURCE,
            diagram=flow(
                ["Nouveau token", "Calcule son Q, K, V", "Ajoute K, V au cache", "Attention"]
            ),
        ),
        CardContent(
            titre="Réduire le coût du KV cache",
            accroche=(
                "Plusieurs leviers permettent de faire tenir plus de contexte et de "
                "requêtes : moins de têtes KV, moins de tokens gardés, des pages mémoire."
            ),
            points=[
                "Multi-query et grouped-query attention partagent les clés et valeurs "
                "entre plusieurs têtes : le cache est divisé par le nombre de groupes.",
                "L'attention à fenêtre glissante ne garde que les derniers tokens, "
                "au prix d'une vision limitée du début.",
                "PagedAttention (vLLM) découpe le cache en pages comme une mémoire "
                "virtuelle : plus de fragmentation, donc plus de requêtes en parallèle.",
                "On peut aussi quantifier le cache en 8 bits, ou réutiliser un préfixe "
                "commun (prompt système) entre requêtes.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Quantization",
            accroche=(
                "Quantifier, c'est stocker poids et parfois activations avec moins de "
                "bits pour réduire la mémoire et accélérer la lecture."
            ),
            points=[
                "Ordre de grandeur : un modèle 7B pèse ~14 Go en fp16, ~7 Go en int8 "
                "et ~3,5 Go en int4, sans compter le cache.",
                "Le post-training quantization (PTQ) se fait sur un modèle déjà "
                "entraîné, avec peu de données ; le QAT réentraîne, plus coûteux mais plus précis.",
                "Le piège : quelques activations aberrantes (outliers) cassent la "
                "quantification naïve ; LLM.int8() et SmoothQuant les traitent.",
                "Méthodes courantes sur les poids : GPTQ et AWQ. En 8 bits la perte "
                "est souvent négligeable, en 4 bits il faut mesurer sur sa tâche.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Batching continu",
            accroche=(
                "Le batching continu insère de nouvelles requêtes dans le batch dès "
                "qu'une autre se termine, au lieu d'attendre la fin du lot."
            ),
            points=[
                "Le batching statique attend la requête la plus longue : les autres "
                "occupent un emplacement vide et le GPU est sous-utilisé.",
                "Le batching continu planifie à chaque itération de decode : une "
                "requête finie libère sa place tout de suite.",
                "Résultat : un débit plusieurs fois supérieur pour une latence "
                "comparable ; c'est le comportement par défaut de vLLM ou TGI.",
                "Compromis : un batch plus grand augmente le débit mais allonge la "
                "latence de chaque requête, d'où un réglage selon le SLO.",
            ],
            source_label=SOURCE,
            diagram=graph(
                [
                    ("q", "File de requêtes", 0, 0),
                    ("s", "Scheduler (chaque itération)", 1, 0),
                    ("g", "GPU : batch en cours", 2, 0),
                ],
                [("q", "s"), ("s", "g", "ajoute"), ("g", "s", "libère")],
            ),
        ),
        CardContent(
            titre="Parallélisme multi-GPU",
            accroche=(
                "Quand le modèle ne tient pas sur un GPU, on le découpe : par couches, "
                "par matrices ou par experts."
            ),
            points=[
                "Ordre de grandeur : 70B en fp16, c'est ~140 Go de poids, plus que "
                "les 80 Go d'un GPU haut de gamme.",
                "Tensor parallelism : on coupe chaque matrice entre GPU, avec des "
                "communications à chaque couche ; à garder dans un nœud (liens rapides).",
                "Pipeline parallelism : chaque GPU porte un groupe de couches ; "
                "efficace entre nœuds mais crée des bulles d'inactivité.",
                "Data parallelism : on duplique le modèle pour servir plus de "
                "requêtes ; les MoE ajoutent l'expert parallelism.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Distillation",
            accroche=(
                "On entraîne un petit modèle à imiter un gros : on garde l'essentiel "
                "de la qualité pour une fraction du coût."
            ),
            points=[
                "L'élève apprend à reproduire les probabilités de l'enseignant "
                "(soft labels), plus riches qu'une simple bonne réponse.",
                "Exemple classique : DistilBERT, environ 40 % plus petit et 60 % plus "
                "rapide que BERT pour ~97 % de ses performances.",
                "Pour les LLM, on distille aussi par données : un gros modèle génère "
                "des réponses ou raisonnements sur lesquels on fine-tune le petit.",
                "Limite : l'élève ne dépasse pas son enseignant, et il faut payer "
                "la génération des données et l'entraînement.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Pruning et sparsité",
            accroche=(
                "Élaguer consiste à supprimer des poids ou des structures peu utiles "
                "pour alléger le modèle."
            ),
            points=[
                "Le pruning non structuré met des poids individuels à zéro : bon "
                "taux de compression, mais peu de gain réel sans support matériel.",
                "Le pruning structuré retire des têtes, des neurones ou des couches "
                "entières : accélération réelle, perte de qualité plus marquée.",
                "Les GPU récents accélèrent la sparsité 2:4 (2 zéros sur 4 poids) "
                "pour environ 2× sur les multiplications de matrices.",
                "Des méthodes comme SparseGPT élaguent un LLM en une passe, sans "
                "réentraînement, jusqu'à ~50 % de poids avec peu de perte.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Speculative decoding",
            accroche=(
                "Un petit modèle devine quelques tokens, le grand modèle les vérifie "
                "tous en une seule passe : on génère plus vite sans changer la sortie."
            ),
            points=[
                "Le modèle brouillon propose k tokens (par exemple 4 à 8) à faible coût.",
                "Le grand modèle calcule en parallèle les probabilités de ces k "
                "positions et accepte le plus long préfixe cohérent.",
                "Un échantillonnage par acceptation/rejet garantit exactement la "
                "même distribution que le grand modèle seul : aucune perte de qualité.",
                "Gain typique de 2 à 3×, qui dépend du taux d'acceptation : "
                "efficace sur du texte prévisible, moins sur du créatif.",
            ],
            source_label=SOURCE,
            diagram=flow(
                ["Brouillon : k tokens", "Grand modèle vérifie", "Garde le préfixe valide"]
            ),
        ),
        CardContent(
            titre="Mixture of Experts (MoE)",
            accroche=(
                "Un MoE remplace le feed-forward par plusieurs experts et n'en active "
                "que quelques-uns par token : beaucoup de paramètres, peu de calcul."
            ),
            points=[
                "Un routeur choisit les k meilleurs experts pour chaque token ; "
                "Mixtral 8x7B en active 2 sur 8.",
                "Chiffres à citer : Mixtral compte ~47 milliards de paramètres au "
                "total mais n'en utilise qu'environ 13 milliards par token.",
                "Le calcul par token suit les paramètres actifs, mais la mémoire "
                "doit contenir tous les experts : il faut plusieurs GPU.",
                "Difficultés : équilibrer la charge entre experts, éviter qu'un "
                "expert soit saturé, et gérer la communication entre GPU.",
            ],
            source_label=SOURCE,
            diagram=graph(
                [
                    ("t", "Token", 0, 1),
                    ("r", "Routeur", 1, 1),
                    ("e1", "Expert 1", 2, 0),
                    ("e2", "Expert 2", 2, 1),
                    ("e3", "Expert N", 2, 2),
                    ("s", "Somme pondérée", 3, 1),
                ],
                [
                    ("t", "r"),
                    ("r", "e1", "top-k"),
                    ("r", "e2", "top-k"),
                    ("r", "e3"),
                    ("e1", "s"),
                    ("e2", "s"),
                ],
            ),
        ),
    ],
)
