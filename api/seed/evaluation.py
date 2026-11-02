"""Contenu du thème Évaluation des LLM (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

SOURCE = "AI Evals FAQ (Hamel Husain)"

THEME = ThemeContent(
    slug="evaluation",
    titre="Évaluation des LLM",
    source_label=SOURCE,
    source_url="https://hamel.dev/blog/posts/evals-faq/",
    cards=[
        CardContent(
            titre="À quoi servent les évals",
            accroche=(
                "Une éval est un test qui vérifie que le produit fait ce que "
                "l'utilisateur et le métier attendent, pas seulement que le modèle est bon."
            ),
            points=[
                "Il faut distinguer les benchmarks publics, qui comparent des "
                "modèles, des évals produit, qui mesurent MON cas d'usage.",
                "Elles servent à décider : changer de modèle, de prompt, de "
                "découpage, en sachant si on progresse ou si on régresse.",
                "Elles font partie du développement, comme le débogage, pas d'un "
                "chantier séparé à planifier plus tard.",
                "Sans évals, on fait des changements à l'intuition et on découvre "
                "les régressions par les utilisateurs.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Commencer par l'analyse d'erreurs",
            accroche=(
                "Avant d'écrire la moindre métrique, je lis des traces réelles et "
                "je note ce qui ne va pas."
            ),
            points=[
                "Étape 1 : relire quelques dizaines de traces et prendre des notes "
                "libres sur chaque défaut observé.",
                "Étape 2 : regrouper ces notes en catégories d'échecs, puis compter "
                "combien de fois chaque catégorie apparaît.",
                "On corrige d'abord les catégories les plus fréquentes ou les plus "
                "graves, au lieu de deviner où est le problème.",
                "Il faut refaire cette analyse après chaque changement important, "
                "avec de nouvelles traces (visée : une centaine par cycle).",
            ],
            source_label=SOURCE,
            diagram=flow(
                ["Traces réelles", "Notes libres", "Catégories d'échecs", "Comptage", "Correction"]
            ),
        ),
        CardContent(
            titre="Construire un jeu de test",
            accroche=(
                "Le jeu de test est un échantillon représentatif des vraies entrées, "
                "complété si besoin par des cas synthétiques bien structurés."
            ),
            points=[
                "Idéal : des traces réelles, échantillonnées au hasard, puis "
                "complétées par des cas rares ou atypiques repérés à part.",
                "Pour démarrer sans données, on génère des cas synthétiques, mais "
                "en variant des dimensions explicites (type d'utilisateur, intention, difficulté).",
                "Prudence avec le synthétique pour les domaines spécialisés ou à "
                "fort enjeu : il manque souvent le réel désordre des utilisateurs.",
                "On versionne le jeu, et on garde une partie intacte (test) qui "
                "ne sert jamais à régler le système.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Vérifications par code d'abord",
            accroche=(
                "Quand une règle suffit pour détecter un défaut, j'écris du code, pas un juge LLM."
            ),
            points=[
                "Exemples : JSON valide, champs obligatoires, longueur maximale, "
                "format de date, absence d'un mot interdit.",
                "Ces assertions sont gratuites, déterministes et rapides : "
                "elles tournent à chaque commit.",
                "Pour du code généré, on exécute les tests ; pour une extraction, "
                "on compare au champ attendu.",
                "Le juge LLM est réservé à ce qui demande du jugement : ton, "
                "pertinence, fidélité à une source.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="LLM-as-judge",
            accroche=(
                "Un juge LLM note automatiquement les sorties sur un critère précis, "
                "à condition d'être cadré et validé."
            ),
            points=[
                "Un juge par mode d'échec (par exemple « cite-t-il une source "
                "inexistante ? »), pas un juge unique pour « la qualité globale ».",
                "Sortie binaire (réussi/échoué) plus une courte justification : "
                "bien plus stable que des notes de 1 à 5.",
                "Le prompt contient la définition du critère, des exemples "
                "positifs et négatifs, et seulement le contexte nécessaire.",
                "On commence avec un modèle puissant, puis on teste un modèle moins "
                "cher contre les mêmes étiquettes humaines.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Valider le juge",
            accroche=(
                "Un juge n'est fiable que s'il est mesuré contre des étiquettes "
                "humaines, comme n'importe quel classifieur."
            ),
            points=[
                "On fait étiqueter un échantillon par un humain, puis on le sépare "
                "en train (exemples du prompt), dev (réglage) et test (verdict final).",
                "On mesure le taux de vrais positifs (échecs bien détectés) et de "
                "vrais négatifs (pas de fausses alertes), pas seulement la précision globale.",
                "En cas de désaccord, on lit d'abord les cas : souvent la consigne "
                "est floue ou l'étiquette humaine discutable.",
                "Le jeu de test du juge reste intact jusqu'au bout pour éviter de se mentir.",
            ],
            source_label=SOURCE,
            diagram=graph(
                [
                    ("h", "Étiquettes humaines", 0, 0),
                    ("j", "Prompt du juge", 1, 0),
                    ("m", "TPR / TNR sur dev", 2, 0),
                ],
                [("h", "j"), ("j", "m"), ("m", "j", "ajuste")],
            ),
        ),
        CardContent(
            titre="Binaire plutôt que notes, et métriques génériques",
            accroche=(
                "Je privilégie des verdicts réussi/échoué sur des critères "
                "précis plutôt que des scores généraux."
            ),
            points=[
                "Les échelles de 1 à 5 sont mal calibrées : deux annotateurs ne "
                "s'accordent pas sur la différence entre un 3 et un 4.",
                "On agrège avec un taux de réussite global, puis on détaille par "
                "critère ou par thème pour savoir quoi corriger.",
                "Les scores génériques (« utilité », BERTScore, ROUGE) mesurent "
                "mal la qualité d'un produit : bons pour repérer des traces à lire, pas pour "
                "décider.",
                "Pour la recherche documentaire, des métriques de similarité ou de rang sont en "
                "revanche pertinentes.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Annotation humaine",
            accroche=(
                "L'humain reste la référence : il faut organiser l'annotation pour "
                "qu'elle soit rapide et cohérente."
            ),
            points=[
                "Nommer un expert du domaine comme référent des décisions de "
                "qualité ; on ajoute des annotateurs seulement si nécessaire, en mesurant leur "
                "accord.",
                "Faciliter la relecture : afficher le contexte et les étapes "
                "intermédiaires, utiliser des raccourcis clavier, montrer l'avancement.",
                "Un notebook ou une petite interface maison suffisent pour démarrer.",
                "L'analyse d'erreurs reste en interne : l'externaliser fait "
                "perdre la compréhension du produit.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Évaluer un RAG ou un agent",
            accroche=(
                "Pour un système à plusieurs étapes, j'évalue chaque étape "
                "séparément avant le résultat final."
            ),
            points=[
                "RAG : d'un côté la recherche (a-t-on retrouvé les bons passages ?), "
                "de l'autre la génération (la réponse s'appuie-t-elle sur eux ?).",
                "Pour la recherche, on utilise des métriques de rang classiques : recall@k, MRR.",
                "Agent ou conversation multi-tours : on cherche à quelle étape "
                "la trajectoire part de travers, et on évalue le passage à un humain.",
                "Cela permet de savoir si l'on doit améliorer le retrieval, le "
                "prompt, le choix d'outil ou le modèle.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Évals en continu : CI et production",
            accroche=(
                "Les évals servent de filet de sécurité à chaque changement, puis "
                "de surveillance en production."
            ),
            points=[
                "En CI : un jeu de régression rapide (assertions et quelques juges) "
                "qui tourne à chaque modification de prompt ou de modèle.",
                "En production : échantillonner des traces réelles, les évaluer, "
                "et alimenter le jeu de test avec les nouveaux échecs.",
                "Ne pas confondre garde-fous, qui bloquent une sortie en temps réel, "
                "et évaluateurs, qui mesurent la qualité souvent en différé.",
                "Pour les parties prenantes : raconter ce qui a changé et pourquoi, "
                "plutôt qu'afficher un tableau de bord générique.",
            ],
            source_label=SOURCE,
        ),
    ],
)
