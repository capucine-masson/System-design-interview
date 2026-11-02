"""Contenu du thème Bonnes pratiques de system design (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

SOURCE = "Principes de bon system design (Sean Goedecke)"

THEME = ThemeContent(
    slug="system-design",
    titre="Bonnes pratiques de system design",
    source_label=SOURCE,
    source_url="https://www.seangoedecke.com/good-system-design/",
    cards=[
        CardContent(
            titre="Un bon design est discret",
            accroche=(
                "Un bon système se reconnaît à ce qu'il ne fait pas parler de lui : "
                "peu d'incidents, peu de surprises."
            ),
            points=[
                "Un design impressionnant mais complexe cache souvent une mauvaise "
                "décision prise tôt, dont on paie ensuite les conséquences.",
                "On part d'un système simple qui fonctionne, puis on ajoute de la "
                "complexité seulement quand un besoin mesuré l'exige.",
                "Message d'entretien : commencer par l'architecture la plus simple, "
                "puis justifier chaque composant ajouté par un problème précis.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Minimiser l'état",
            accroche=(
                "L'état est ce qui rend les systèmes difficiles : on peut redémarrer "
                "un service sans état, pas une base corrompue."
            ),
            points=[
                "Un composant avec état peut se corrompre et ne se répare pas "
                "par un simple redémarrage ; il demande sauvegardes et soin.",
                "Règle : un seul service est propriétaire de la base ; les autres "
                "passent par son API ou consomment ses événements.",
                "Les services sans état se répliquent facilement derrière un "
                "équilibreur de charge.",
                "Chaque nouvelle source de vérité (cache, copie, index externe) "
                "est un état de plus à garder cohérent.",
            ],
            source_label=SOURCE,
            diagram=graph(
                [
                    ("a", "Service A", 0, 0),
                    ("b", "Service B", 0, 2),
                    ("s", "Service propriétaire", 1, 1),
                    ("d", "Base de données", 2, 1),
                ],
                [("a", "s", "API"), ("b", "s", "API"), ("s", "d")],
            ),
        ),
        CardContent(
            titre="Schémas et index",
            accroche=(
                "Un schéma lisible et des index adaptés évitent la plupart des "
                "problèmes de performance."
            ),
            points=[
                "Concevoir le schéma avec soin : flexible mais clair, sans table "
                "fourre-tout de type clé-valeur ou colonne JSON pour tout.",
                "Un index suit les requêtes réelles ; pour un index composé, on "
                "place d'abord la colonne la plus sélective.",
                "Les index accélèrent les lectures mais ralentissent les écritures "
                "et prennent de la place : on les choisit, on ne les empile pas.",
                "Avant d'ajouter un cache, regarder si un index manquant explique la lenteur.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Laisser la base de données travailler",
            accroche=(
                "Une base sait faire des jointures et filtrer bien mieux que du code applicatif."
            ),
            points=[
                "Préférer une jointure à des allers-retours multiples ; éviter le "
                "problème N+1 (une requête par élément d'une liste).",
                "Envoyer les lectures aux réplicas pour soulager la base principale.",
                "Limiter le débit des écritures en masse et des grosses "
                "transactions, qui peuvent saturer la base principale.",
                "Mesurer avec EXPLAIN avant d'optimiser : on corrige ce que l'on a vu.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Sortir le travail lent de la requête",
            accroche=(
                "Une requête utilisateur renvoie vite le minimum utile ; le reste "
                "part en tâche de fond."
            ),
            points=[
                "Exemples : envoi d'email, génération de rapport, appel à une API "
                "tierce lente, appel à un LLM long.",
                "Mécanisme par défaut : une file de tâches avec des workers, qui "
                "gère aussi les nouvelles tentatives.",
                "Pour des tâches planifiées très loin dans le temps, une table en "
                "base avec une vérification périodique est plus simple.",
                "Il faut prévoir l'état visible de la tâche (en cours, réussie, "
                "échouée) pour l'utilisateur.",
            ],
            source_label=SOURCE,
            diagram=flow(["Requête", "Réponse rapide", "File de tâches", "Worker"]),
        ),
        CardContent(
            titre="Utiliser un cache avec parcimonie",
            accroche=(
                "Un cache est un état supplémentaire qui peut devenir périmé : "
                "je le mets en dernier recours."
            ),
            points=[
                "Premier réflexe : trouver pourquoi c'est lent (index, requête, "
                "appel inutile) avant de cacher.",
                "Un cache amène des questions : quand l'invalider, que se passe-t-il "
                "au démarrage à froid, comment éviter les données périmées.",
                "Si on cache, définir une durée de vie claire et accepter explicitement "
                "l'obsolescence possible.",
                "Un stockage d'objets peut servir de grand cache persistant pour "
                "des données lourdes et rarement modifiées.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Événements, appels directs, push et pull",
            accroche=(
                "Les événements sont puissants mais plus difficiles à suivre : je "
                "les choisis pour des besoins précis."
            ),
            points=[
                "Événements : adaptés aux notifications sans réponse attendue et "
                "aux gros volumes peu urgents.",
                "Appels directs : plus faciles à tracer et à raisonner, donc "
                "préférables dans la plupart des cas.",
                "Pull (le consommateur demande) est plus simple ; push convient "
                "à des données rarement modifiées qui doivent atteindre beaucoup de monde.",
                "À très grande échelle, le push passe par des files et des "
                "workers qui diffusent aux destinataires.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Soigner les chemins critiques",
            accroche=(
                "Je concentre l'effort sur les parcours les plus fréquentés et les plus importants."
            ),
            points=[
                "Identifier les flux qui rapportent de l'argent ou touchent "
                "le plus d'utilisateurs : ce sont eux qui méritent le plus de soin.",
                "Sur ces chemins, peu de designs sont bons, et une erreur coûte "
                "bien plus cher qu'ailleurs.",
                "Pour le reste, une solution simple et pas parfaite suffit.",
                "Dans un entretien, annoncer d'emblée quel est le chemin critique "
                "et le dimensionner en priorité.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Journaliser et mesurer",
            accroche=(
                "On ne corrige pas ce qu'on ne voit pas : logs et métriques "
                "décident de la vitesse de diagnostic."
            ),
            points=[
                "Journaliser les décisions prises, surtout sur les chemins "
                "d'échec ou inhabituels, pas seulement les erreurs.",
                "Suivre les ressources et les files d'attente : saturation CPU, "
                "mémoire, retard des queues.",
                "Regarder les latences p95 et p99 plutôt que la moyenne, qui "
                "cache les pires expériences.",
                "Ne pas journaliser de données sensibles.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Prévoir les pannes",
            accroche=(
                "Tout composant finira par tomber : je décide à l'avance comment le système réagit."
            ),
            points=[
                "Interrupteurs de secours (killswitch) pour désactiver une "
                "fonctionnalité qui pose problème sans redéployer.",
                "Nouvelles tentatives prudentes : délai croissant, disjoncteur "
                "(circuit breaker) et clés d'idempotence pour ne pas dupliquer l'action.",
                "Choisir par fonctionnalité si on échoue ouvert (par exemple une "
                "limitation de débit qui laisse passer) ou fermé (une authentification qui "
                "refuse).",
                "Tester ces comportements : une panne simulée vaut mieux qu'une "
                "surprise en production.",
            ],
            source_label=SOURCE,
        ),
        CardContent(
            titre="Préférer des composants éprouvés",
            accroche=(
                "Un bon design applique des outils bien connus aux bons endroits, il n'invente pas."
            ),
            points=[
                "Une base relationnelle, une file de tâches, un cache standard "
                "couvrent la grande majorité des besoins.",
                "Le code maison pour ce qu'un outil éprouvé fait déjà ajoute de la "
                "maintenance et des bugs.",
                "On gagne en recrutement, en documentation et en fiabilité en "
                "restant sur des technologies répandues.",
                "Justifier tout écart : « pourquoi pas la solution standard ? » "
                "doit avoir une réponse mesurée.",
            ],
            source_label=SOURCE,
        ),
    ],
)
