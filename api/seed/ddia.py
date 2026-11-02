"""Contenu du thème Systèmes de données (texte original, à dire à l'oral).

Numérotation des chapitres : 1re édition de « Designing Data-Intensive Applications ».
"""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

BOOK = "Martin Kleppmann, Designing Data-Intensive Applications (O'Reilly)"


def _ch(numero: int, titre: str) -> str:
    """Libellé de source d'un chapitre (sans lien)."""
    return f"DDIA (1re éd.), ch. {numero} : {titre}"


THEME = ThemeContent(
    slug="ddia",
    titre="Systèmes de données",
    source_label=BOOK,
    source_url=None,
    cards=[
        CardContent(
            titre="Fiabilité, scalabilité, maintenabilité",
            accroche=(
                "Trois qualités structurent tout système de données : qu'il continue "
                "de marcher malgré les pannes, qu'il tienne la charge, qu'il reste évolutif."
            ),
            points=[
                "Fiabilité : une faute (un composant qui dévie) n'est pas une "
                "défaillance (le service s'arrête) ; on conçoit pour tolérer les fautes.",
                "Scalabilité : on décrit la charge par des paramètres (requêtes par "
                "seconde, ratio lectures/écritures) puis on mesure la performance.",
                "Pour la latence, on regarde les percentiles (p95, p99), pas la moyenne : "
                "les pires requêtes sont souvent celles des meilleurs clients.",
                "Exemple classique : le fil d'actualité d'un réseau social, où "
                "précalculer le fil à l'écriture (fan-out) coûte cher pour les comptes très "
                "suivis.",
                "Maintenabilité : simplicité, opérabilité et évolutivité pour les "
                "équipes qui vivront avec le système.",
            ],
            source_label=_ch(1, "Reliable, Scalable, and Maintainable Applications"),
        ),
        CardContent(
            titre="Modèles de données",
            accroche=(
                "Le choix du modèle (relationnel, document, graphe) détermine ce "
                "qui est simple ou pénible à exprimer."
            ),
            points=[
                "Relationnel : jointures, schéma strict à l'écriture, bon pour des "
                "relations nombreuses entre entités.",
                "Document : données auto-contenues (un profil et ses sous-éléments), "
                "schéma souple à la lecture, bonne localité ; moins adapté aux relations "
                "plusieurs-à-plusieurs.",
                "Graphe : quand tout est relation (réseaux sociaux, recommandations) "
                "et que les parcours sont de profondeur variable.",
                "Les modèles se rapprochent : les bases relationnelles stockent du "
                "JSON, les bases de documents font des jointures.",
            ],
            source_label=_ch(2, "Data Models and Query Languages"),
        ),
        CardContent(
            titre="Stockage : B-tree contre LSM-tree",
            accroche=(
                "Deux grandes familles de moteurs de stockage, avec des compromis "
                "différents entre lecture et écriture."
            ),
            points=[
                "B-tree : pages de taille fixe mises à jour sur place, avec un journal "
                "(WAL) pour la reprise ; lectures prévisibles, très répandu en OLTP.",
                "LSM-tree : on écrit en mémoire puis on vide en fichiers triés "
                "immuables fusionnés en tâche de fond (compaction) ; écritures séquentielles "
                "rapides.",
                "Compromis : le LSM écrit plus vite mais coûte de la compaction et "
                "peut avoir une latence de lecture moins stable ; le B-tree lit bien.",
                "OLTP contre OLAP : les analyses lisent beaucoup de lignes sur peu "
                "de colonnes, d'où les stockages en colonnes compressés.",
            ],
            source_label=_ch(3, "Storage and Retrieval"),
            diagram=graph(
                [
                    ("w", "Écriture", 0, 0),
                    ("m", "Memtable (mémoire)", 1, 0),
                    ("s", "Fichiers triés (SSTable)", 2, 0),
                    ("c", "Compaction", 3, 0),
                ],
                [("w", "m"), ("m", "s", "flush"), ("s", "c")],
            ),
        ),
        CardContent(
            titre="Encodage et évolution des schémas",
            accroche=(
                "Dans un système qui évolue, l'ancien et le nouveau code coexistent : "
                "les formats de données doivent rester compatibles."
            ),
            points=[
                "Compatibilité ascendante : le nouveau code lit les anciennes "
                "données ; descendante : l'ancien code lit les nouvelles.",
                "Les mises à jour progressives (rolling upgrade) obligent les deux à coexister.",
                "JSON est lisible mais ambigu et verbeux ; Protocol Buffers ou "
                "Avro sont compacts et gèrent l'évolution du schéma.",
                "Règles pratiques : ajouter des champs optionnels, ne jamais "
                "réutiliser un identifiant de champ supprimé.",
            ],
            source_label=_ch(4, "Encoding and Evolution"),
        ),
        CardContent(
            titre="Réplication",
            essentielle=True,
            accroche=(
                "Répliquer, c'est garder plusieurs copies des données pour la "
                "disponibilité, la latence et le débit de lecture."
            ),
            points=[
                "Leader-follower : toutes les écritures passent par le leader, les "
                "suiveurs répliquent ; lectures réparties sur les suiveurs.",
                "Synchrone : on attend la copie, donc durabilité mais risque de blocage ; "
                "asynchrone : rapide mais on peut perdre des écritures si le leader tombe.",
                "Le retard de réplication cause des anomalies : relire sa propre "
                "écriture ne marche plus, ou les lectures semblent revenir dans le passé.",
                "Multi-leader : écritures dans plusieurs sites mais conflits à résoudre.",
                "Sans leader (style Dynamo) : quorums avec w + r > n pour que lecture "
                "et écriture se recoupent.",
            ],
            source_label=_ch(5, "Replication"),
            diagram=graph(
                [
                    ("c", "Client", 0, 1),
                    ("l", "Leader", 1, 1),
                    ("f1", "Suiveur 1", 2, 0),
                    ("f2", "Suiveur 2", 2, 2),
                ],
                [("c", "l", "écritures"), ("l", "f1", "log"), ("l", "f2", "log")],
            ),
        ),
        CardContent(
            titre="Partitionnement",
            essentielle=True,
            accroche=(
                "Quand les données dépassent une machine, on les découpe en "
                "partitions réparties sur plusieurs nœuds."
            ),
            points=[
                "Par intervalle de clés : bon pour les requêtes par plage, mais "
                "risque de point chaud (par exemple tout l'horodatage récent au même endroit).",
                "Par hachage de la clé : répartition uniforme, mais on perd les "
                "requêtes par plage.",
                "Index secondaires : locaux à chaque partition (écriture simple, "
                "lecture sur toutes les partitions) ou globaux (lecture ciblée, écriture plus "
                "coûteuse).",
                "Rééquilibrage : beaucoup de partitions fixes plutôt que hacher "
                "modulo le nombre de nœuds, qui déplacerait presque tout.",
                "Routage : le client, un proxy ou un service de coordination doit "
                "savoir quelle partition contient la clé.",
            ],
            source_label=_ch(6, "Partitioning"),
        ),
        CardContent(
            titre="Transactions et isolation",
            essentielle=True,
            accroche=(
                "Une transaction regroupe plusieurs opérations en une unité "
                "tout-ou-rien ; l'isolation précise ce que voient les transactions concurrentes."
            ),
            points=[
                "ACID : atomicité (tout ou rien), cohérence (règles métier "
                "respectées), isolation, durabilité.",
                "Read committed : pas de lecture de données non validées. Snapshot "
                "isolation : chaque transaction voit une photo cohérente de la base.",
                "Anomalies à citer : mise à jour perdue, write skew (deux "
                "transactions lisent puis écrivent des éléments différents en violant une règle "
                "commune) et fantômes.",
                "Seule la sérialisabilité les évite toutes : exécution en série, "
                "verrouillage en deux phases ou isolation sérialisable optimiste (SSI).",
            ],
            source_label=_ch(7, "Transactions"),
        ),
        CardContent(
            titre="Les problèmes des systèmes distribués",
            accroche=(
                "Dans un système distribué, une partie peut tomber sans que le reste "
                "le sache : on ne peut pas se fier au réseau ni aux horloges."
            ),
            points=[
                "Le réseau perd, retarde ou duplique des messages ; un timeout ne "
                "dit pas si la requête a été traitée.",
                "Les horloges des machines dérivent : on ne peut pas ordonner des "
                "événements de machines différentes avec des horodatages.",
                "Une pause (ramasse-miettes, gel de VM) peut faire croire qu'un nœud "
                "est mort, ou lui faire croire qu'il est encore leader.",
                "Parade : jetons de fencing, qui permettent à la ressource de refuser "
                "un ancien détenteur de verrou.",
                "On raisonne en pannes partielles : certaines parties marchent, d'autres non.",
            ],
            source_label=_ch(8, "The Trouble with Distributed Systems"),
        ),
        CardContent(
            titre="Cohérence et consensus",
            essentielle=True,
            accroche=(
                "Pour que plusieurs nœuds s'accordent, on utilise des garanties "
                "de cohérence fortes et des algorithmes de consensus."
            ),
            points=[
                "Linéarisabilité : le système se comporte comme s'il n'y avait "
                "qu'une copie ; coûteuse en latence et en disponibilité.",
                "Cohérence causale : ordre respecté uniquement entre événements "
                "liés ; plus faible mais plus disponible.",
                "Le consensus (Raft, Paxos, Zab) sert à élire un leader, "
                "verrouiller, valider un ordre total ; il tolère la panne d'une minorité de nœuds.",
                "Validation atomique à deux phases (2PC) : un coordinateur, "
                "bloquant s'il tombe au mauvais moment.",
                "Théorème CAP à nuancer : en cas de partition, il faut choisir entre "
                "cohérence et disponibilité.",
            ],
            source_label=_ch(9, "Consistency and Consensus"),
        ),
        CardContent(
            titre="Traitement par lots",
            accroche=(
                "Le batch lit un gros jeu de données d'entrée fixe et produit une "
                "sortie dérivée, sans modifier l'entrée."
            ),
            points=[
                "MapReduce : on applique une fonction à chaque enregistrement (map), "
                "puis on regroupe par clé pour agréger (reduce).",
                "Les moteurs de flux de données (Spark, Flink) généralisent cette "
                "idée sans écrire sur disque entre chaque étape.",
                "Entrées immuables et sorties dérivées : on peut relancer un job "
                "après un bug sans corrompre les données.",
                "Cas d'usage : construire des index de recherche, des modèles, des "
                "rapports ; la latence se compte en minutes ou en heures.",
            ],
            source_label=_ch(10, "Batch Processing"),
            diagram=flow(
                ["Entrée immuable", "Map", "Regroupement par clé", "Reduce", "Sortie dérivée"]
            ),
        ),
        CardContent(
            titre="Traitement de flux",
            accroche=(
                "Le streaming traite les événements au fil de l'eau, avec un journal "
                "ordonné comme colonne vertébrale."
            ),
            points=[
                "Journal d'événements (Kafka) : une suite ordonnée, partitionnée "
                "et rejouable ; les consommateurs lisent à leur rythme.",
                "Change data capture : on transforme les changements d'une base "
                "en flux, pour alimenter un cache, un index, un entrepôt.",
                "Event sourcing : le journal des événements est la source de "
                "vérité, l'état courant en est une vue dérivée.",
                "Livraison au moins une fois plus idempotence donne un effet "
                "pratiquement exactement une fois.",
                "Fenêtres de temps et événements en retard sont les vraies difficultés.",
            ],
            source_label=_ch(11, "Stream Processing"),
        ),
    ],
)
