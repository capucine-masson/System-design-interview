"""Catalogue des types de cas de system design : ajouter un cas = ajouter une entrée ici."""

from typing import Literal

from pydantic import BaseModel

from api.lang import Lang
from api.sd_catalog_en import CASE_TEXTS_EN

Famille = Literal["ml", "classique"]


class CaseType(BaseModel):
    """Un type de cas proposé au candidat (famille « ml » par défaut)."""

    slug: str
    famille: Famille = "ml"
    titre: str
    description: str
    axes: list[str]

    def localized(self, lang: Lang) -> "CaseType":
        """Copie du type avec titre, description et axes dans la langue demandée."""
        text = CASE_TEXTS_EN.get(self.slug)
        if lang == "fr" or text is None:
            return self
        return self.model_copy(
            update={"titre": text.titre, "description": text.description, "axes": text.axes}
        )


CASE_TYPES: list[CaseType] = [
    CaseType(
        slug="rag",
        titre="RAG sur une grande base documentaire",
        description="Répondre à des questions sur un très grand corpus de documents internes.",
        axes=[
            "volume et mise à jour des documents",
            "chunking et embeddings",
            "base vectorielle et reranking",
            "évaluation du retrieval",
            "hallucinations et citations",
            "droits d'accès",
        ],
    ),
    CaseType(
        slug="inference",
        titre="Service d'inférence LLM à grande échelle",
        description="Servir un LLM à beaucoup d'utilisateurs, avec latence et coût contraints.",
        axes=[
            "trafic et pics de charge",
            "latence au premier token contre débit",
            "GPU, batching continu, KV cache",
            "quantization",
            "autoscaling et streaming",
            "coût par token",
        ],
    ),
    CaseType(
        slug="entrainement",
        titre="Pipeline d'entraînement ou de fine-tuning",
        description="Entraîner ou adapter un modèle sur des données propriétaires.",
        axes=[
            "collecte, nettoyage et déduplication des données",
            "taille du modèle et budget de calcul",
            "parallélisme data, tensor, pipeline",
            "checkpointing et reprise sur panne",
            "LoRA contre full fine-tuning",
            "évaluation avant déploiement",
        ],
    ),
    CaseType(
        slug="evaluation",
        titre="Plateforme d'évaluation de LLM",
        description="Mesurer de façon fiable la qualité de modèles et de prompts en continu.",
        axes=[
            "benchmarks et jeux de test internes",
            "LLM-as-judge et sa validation",
            "évaluation humaine",
            "détection de régressions",
            "A/B tests en production",
            "coût et fréquence des évaluations",
        ],
    ),
    CaseType(
        slug="agent",
        titre="Agent ou assistant avec outils",
        description="Un assistant qui planifie et appelle des outils pour accomplir des tâches.",
        axes=[
            "outils et permissions",
            "mémoire et contexte",
            "garde-fous et actions irréversibles",
            "fiabilité sur plusieurs étapes",
            "observabilité et évaluation",
            "latence et coût par tâche",
        ],
    ),
    CaseType(
        slug="recommandation",
        titre="Recommandation ou modération avec ML",
        description="Un système ML qui classe ou filtre du contenu en continu.",
        axes=[
            "volume d'événements et latence de décision",
            "feature store et données en ligne/hors ligne",
            "entraînement et déploiement des modèles",
            "monitoring et dérive des données",
            "faux positifs, équité et boucle humaine",
            "démarrage à froid",
        ],
    ),
    CaseType(
        slug="google-docs",
        famille="classique",
        titre="Éditeur de documents collaboratif (type Google Docs)",
        description="Plusieurs personnes éditent le même document en temps réel.",
        axes=[
            "nombre d'éditeurs simultanés et taille des documents",
            "résolution des conflits (OT ou CRDT)",
            "synchronisation temps réel et mode hors ligne",
            "historique des versions et restauration",
            "droits de partage et commentaires",
            "stockage et reprise après panne",
        ],
    ),
    CaseType(
        slug="streaming-video",
        famille="classique",
        titre="Streaming vidéo à la demande (type Netflix, YouTube)",
        description="Diffuser des vidéos à des millions de spectateurs dans le monde.",
        axes=[
            "catalogue, durée et volume de vidéos",
            "encodage multi-résolutions et débit adaptatif",
            "CDN et caches en périphérie",
            "pics de trafic lors des sorties",
            "reprise de lecture et recommandations",
            "coût de stockage et de bande passante",
        ],
    ),
    CaseType(
        slug="url-shortener",
        famille="classique",
        titre="Raccourcisseur d'URL",
        description="Transformer de longues URL en liens courts et rediriger rapidement.",
        axes=[
            "créations et redirections par seconde",
            "génération d'identifiants uniques",
            "durée de vie et expiration des liens",
            "cache et latence de redirection",
            "statistiques de clics",
            "abus et liens malveillants",
        ],
    ),
    CaseType(
        slug="messagerie",
        famille="classique",
        titre="Messagerie instantanée (type WhatsApp)",
        description="Envoyer des messages entre utilisateurs, en direct et en groupe.",
        axes=[
            "utilisateurs connectés et messages par seconde",
            "connexions persistantes (WebSocket)",
            "ordre, livraison garantie et accusés de lecture",
            "groupes et diffusion",
            "stockage de l'historique",
            "présence et notifications hors ligne",
        ],
    ),
    CaseType(
        slug="fil-actualite",
        famille="classique",
        titre="Fil d'actualité d'un réseau social (type X, Instagram)",
        description="Afficher à chacun un fil de publications de ses relations.",
        axes=[
            "utilisateurs, publications et lectures par seconde",
            "diffusion à l'écriture ou à la lecture (fan-out)",
            "comptes très suivis",
            "classement du fil",
            "médias et cache",
            "cohérence et fraîcheur",
        ],
    ),
    CaseType(
        slug="vtc",
        famille="classique",
        titre="Service de VTC (type Uber)",
        description="Mettre en relation passagers et chauffeurs proches, en temps réel.",
        axes=[
            "chauffeurs actifs et fréquence des positions",
            "index géospatial et recherche de proximité",
            "appariement et gestion des pics",
            "suivi de course en temps réel",
            "tarification dynamique",
            "tolérance aux pannes et paiement",
        ],
    ),
    CaseType(
        slug="stockage-fichiers",
        famille="classique",
        titre="Stockage et synchronisation de fichiers (type Dropbox)",
        description="Stocker des fichiers et les synchroniser entre plusieurs appareils.",
        axes=[
            "utilisateurs, volume stocké et taille des fichiers",
            "découpage en blocs et déduplication",
            "synchronisation et gestion des conflits",
            "partage et permissions",
            "versions et corbeille",
            "durabilité et coût du stockage",
        ],
    ),
    CaseType(
        slug="rate-limiter",
        famille="classique",
        titre="Limiteur de débit distribué",
        description="Limiter le nombre de requêtes par client sur une API répartie.",
        axes=[
            "requêtes par seconde et nombre de clients",
            "algorithmes (fenêtre glissante, seau à jetons)",
            "état partagé et cohérence entre nœuds",
            "latence ajoutée à chaque requête",
            "règles par client ou par route",
            "comportement en cas de panne",
        ],
    ),
    CaseType(
        slug="notifications",
        famille="classique",
        titre="Système de notifications (push, email, SMS)",
        description="Envoyer des notifications fiables à des millions d'utilisateurs.",
        axes=[
            "volume d'envois et pics de campagne",
            "files d'attente et priorités",
            "préférences et désabonnements",
            "nouvelles tentatives et idempotence",
            "limites des fournisseurs externes",
            "suivi de livraison",
        ],
    ),
    CaseType(
        slug="autocompletion",
        famille="classique",
        titre="Suggestion de recherche (autocomplétion)",
        description="Proposer des suggestions pendant que l'utilisateur tape sa requête.",
        axes=[
            "requêtes par seconde et latence cible",
            "structure de données (arbre de préfixes)",
            "classement par popularité et fraîcheur",
            "mise à jour des suggestions",
            "personnalisation",
            "contenus à filtrer",
        ],
    ),
    CaseType(
        slug="crawler",
        famille="classique",
        titre="Robot d'exploration du web (web crawler)",
        description="Parcourir et télécharger des pages web à grande échelle.",
        axes=[
            "nombre de pages et fréquence de rafraîchissement",
            "file d'URL et priorités",
            "politesse envers les sites (robots.txt)",
            "détection de doublons",
            "tolérance aux pannes et reprise",
            "stockage et traitement des pages",
        ],
    ),
    CaseType(
        slug="paiement",
        famille="classique",
        titre="Système de paiement en ligne (type Stripe)",
        description="Traiter des paiements de façon fiable, sans débit en double.",
        axes=[
            "transactions par seconde et pics",
            "idempotence et prévention des doubles débits",
            "cohérence et transactions distribuées",
            "intégration avec banques et fournisseurs",
            "rapprochement comptable",
            "sécurité et conformité",
        ],
    ),
    CaseType(
        slug="billetterie",
        famille="classique",
        titre="Réservation de billets (type Ticketmaster)",
        description="Vendre des places limitées lors d'événements très demandés.",
        axes=[
            "pic de demandes à l'ouverture de la vente",
            "réservation temporaire et expiration",
            "éviter la survente (concurrence)",
            "file d'attente virtuelle",
            "paiement et annulation",
            "équité face aux robots",
        ],
    ),
    CaseType(
        slug="kv-store",
        famille="classique",
        titre="Base clé-valeur distribuée",
        description="Concevoir un stockage clé-valeur réparti, rapide et tolérant aux pannes.",
        axes=[
            "volume de données et opérations par seconde",
            "partitionnement et rééquilibrage",
            "réplication et niveaux de cohérence",
            "tolérance aux pannes et reprise",
            "latence en lecture et en écriture",
            "compactage et stockage sur disque",
        ],
    ),
    CaseType(
        slug="sessions-utilisateur",
        famille="classique",
        titre="Gestion des sessions utilisateur (connexion, déconnexion, expiration)",
        description="Authentifier des utilisateurs et gérer leurs sessions de façon sûre.",
        axes=[
            "utilisateurs actifs et connexions par seconde",
            "sessions serveur ou jetons (JWT)",
            "stockage des sessions (cache partagé)",
            "expiration, renouvellement et déconnexion sur tous les appareils",
            "vol de session et sécurité",
            "tolérance aux pannes et montée en charge",
        ],
    ),
    CaseType(
        slug="permissions",
        famille="classique",
        titre="Gestion des permissions (rôles et contrôle d'accès)",
        description="Décider qui peut faire quoi sur quelles ressources, dans une organisation.",
        axes=[
            "utilisateurs, ressources et vérifications par seconde",
            "modèle d'accès (RBAC, ABAC, héritage)",
            "latence des vérifications et cache",
            "révocation et propagation des changements",
            "journal d'audit",
            "administration et délégation des droits",
        ],
    ),
    CaseType(
        slug="commandes-en-ligne",
        famille="classique",
        titre="Commandes en ligne avec panier (type e-commerce)",
        description="Gérer le panier, la création, le suivi et l'annulation de commandes.",
        axes=[
            "commandes par seconde et pics (soldes)",
            "panier et réservation du stock",
            "états de la commande et suivi",
            "annulation, remboursement et cohérence",
            "paiement et idempotence",
            "notifications et intégration logistique",
        ],
    ),
    CaseType(
        slug="bibliotheque",
        famille="classique",
        titre="Gestion d'une bibliothèque de livres",
        description="Ajouter, retirer et rechercher des livres, et gérer les emprunts.",
        axes=[
            "nombre de livres, d'exemplaires et d'utilisateurs",
            "modèle de données (livre, exemplaire, emprunt)",
            "recherche par titre, auteur ou sujet",
            "emprunts, retours et réservations",
            "concurrence sur un même exemplaire",
            "multi-sites et évolution du catalogue",
        ],
    ),
    CaseType(
        slug="blog",
        famille="classique",
        titre="Plateforme de blog",
        description="Créer, modifier, supprimer et publier des articles lus par beaucoup de monde.",
        axes=[
            "auteurs, articles et lectures par seconde",
            "modèle de données et brouillons",
            "cache et diffusion des pages publiées",
            "recherche, tags et commentaires",
            "éditeur, médias et versions",
            "modération et sécurité du contenu",
        ],
    ),
    CaseType(
        slug="moe-serving",
        titre="Serving d'un modèle Mixture-of-Experts de 70B avec cible de latence p95",
        description="Servir un gros MoE à beaucoup d'utilisateurs en tenant une latence p95.",
        axes=[
            "trafic, longueur des prompts et cible de latence p95",
            "routage des experts et équilibrage de charge",
            "expert, tensor et pipeline parallelism entre GPU",
            "budget mémoire GPU (poids, KV cache, activations)",
            "batching continu et compromis latence contre débit",
            "quantization, pannes de GPU et coût par token",
        ],
    ),
    CaseType(
        slug="api-multi-tenant",
        titre="Limitation de débit et allocation de capacité d'une API LLM multi-tenant",
        description="Répartir équitablement la capacité GPU entre des clients aux SLA différents.",
        axes=[
            "clients, paliers de SLA et capacité GPU disponible",
            "quotas en tokens et en requêtes par minute",
            "équité entre clients (noisy neighbor) et files prioritaires",
            "rafales, rejet contre mise en file, dégradation gracieuse",
            "état partagé des compteurs entre régions et latence ajoutée",
            "mesure, facturation et alertes par client",
        ],
    ),
    CaseType(
        slug="lora-multi-adaptateurs",
        titre="Fine-tuning et serving multi-adaptateurs LoRA pour des clients",
        description="Proposer à chaque client son modèle adapté sans un GPU dédié par client.",
        axes=[
            "nombre de clients et taille des jeux de données",
            "pipeline de fine-tuning LoRA et évaluation avant mise en ligne",
            "un modèle de base partagé et des adaptateurs chargés à la demande",
            "mémoire GPU, cache d'adaptateurs et démarrage à froid",
            "isolation des données et des performances entre clients",
            "versions, retour arrière et coût par client",
        ],
    ),
]


def get_case_type(slug: str) -> CaseType | None:
    """Retourne le type de cas correspondant au slug, s'il existe."""
    return next((case_type for case_type in CASE_TYPES if case_type.slug == slug), None)
