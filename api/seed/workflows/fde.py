"""Catégorie Mises en situation FDE : questions de client et plan de réponse."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow
from api.seed.workflows.common import OVERVIEW, SOURCE, doc

THEME = ThemeContent(
    slug="fde",
    titre="Mises en situation FDE",
    source_label=SOURCE,
    source_url=OVERVIEW,
    cards=[
        CardContent(
            titre="« Automatiser un KYC avec validation humaine »",
            essentielle=True,
            accroche=(
                "Je découpe en activities, j'attends la validation humaine avec un timeout, "
                "et je garde tout dans l'historique."
            ),
            points=[
                "Activities : extraction des documents, contrôle sanctions/PEP, règles métier.",
                "wait_condition avec timeout pour l'approbation, signal pour la décision.",
                "Escalade si pas de réponse à temps, et branche de refus.",
                "Traçabilité : l'historique garde qui a décidé et quand.",
                "Chiffrement des payloads, workers dans le VPC du client.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/building-workflows/waiting_for_conditions"),
            diagram=flow(["Extraction", "Sanctions / PEP", "Règles", "Validation humaine"]),
        ),
        CardContent(
            titre="« Aucune donnée ne doit sortir de notre réseau »",
            essentielle=True,
            accroche=(
                "L'architecture hybride répond à ça : le code et les données restent chez "
                "le client, Mistral n'orchestre que."
            ),
            points=[
                "Hybride : workers et code chez le client, orchestrateur chez Mistral.",
                "Chiffrement AES-GCM dans le SDK : la plateforme ne voit que du chiffré.",
                "Offloading des gros payloads dans le blob storage du client.",
                "Les workers se connectent vers l'orchestrateur, flux sortants uniquement.",
                "Pour aller plus loin : orchestrateur on-prem ou cloud privé, à confirmer "
                "avec Mistral.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/overview"),
        ),
        CardContent(
            titre="« Le workflow est lent ou coûte cher »",
            accroche=(
                "Je cherche d'abord où se perd le temps, puis je parallélise, je réduis les "
                "tokens et je cache."
            ),
            points=[
                "Mesurer d'abord : traces par activity dans Studio.",
                "Paralléliser les activities indépendantes.",
                "Réduire les tokens envoyés au LLM.",
                "Cacher les résultats qui se répètent.",
                "Petit modèle pour les étapes simples, gros modèle pour les difficiles.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/observability"),
        ),
        CardContent(
            titre="« Un job tourne depuis 3 semaines et l'historique explose »",
            essentielle=True,
            accroche=(
                "L'historique est limité. J'utilise continue_as_new pour repartir à zéro en "
                "gardant l'état utile."
            ),
            points=[
                "Limite : environ 51 200 événements ou 50 Mo d'historique.",
                "should_continue_as_new() dit quand on s'en approche.",
                "continue_as_new relance avec un historique vide et l'état reporté.",
                "Ne reporter que l'état utile, pas tout l'historique.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/building-workflows/continue_as_new"),
        ),
        CardContent(
            titre="« Comment mettre à jour un workflow en production ? »",
            accroche=(
                "Le versioning n'est pas couvert par la doc lue. Je propose un nouveau "
                "deployment en parallèle, puis je vide l'ancien."
            ),
            points=[
                "Honnêteté : le versioning n'est pas documenté dans ce que j'ai lu.",
                "Proposition : déployer la nouvelle version dans un nouveau deployment.",
                "Router les nouvelles exécutions avec deployment_name.",
                "Laisser finir les exécutions en cours sur l'ancien, puis le retirer.",
                "Attention : deux deployments actifs avec le même workflow donnent un 409.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/managing-workflows-in-production/deployments"),
        ),
        CardContent(
            titre="« Comment testez-vous un workflow ? »",
            accroche=(
                "Les activities se testent comme des fonctions Python. Le workflow s'exécute "
                "en local avec un worker."
            ),
            points=[
                "Activities : des fonctions Python normales, testables avec pytest.",
                "Workflow : exécution locale avec un worker en self-hosted.",
                "Utiliser un DEPLOYMENT_NAME de test pour ne pas voler les runs de prod.",
                "La doc lue ne décrit pas de framework de test dédié : ne pas en inventer.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/concepts/workers"),
        ),
        CardContent(
            titre="« Qu'est-ce qui vous manque dans le produit ? »",
            accroche=(
                "Le produit est en public preview. Je liste honnêtement ce que la doc ne "
                "couvre pas encore."
            ),
            points=[
                "Pas de quotas ni de tarification documentés.",
                "Valeurs par défaut des retries non précisées.",
                "Quelques incohérences de doc (par exemple « ~50K » contre 51 200 événements).",
                "Versioning des workflows non documenté.",
            ],
            source_label=SOURCE,
            source_url=OVERVIEW,
        ),
        CardContent(
            titre="« Le LLM échoue ou hallucine à l'étape 7 sur 10 »",
            essentielle=True,
            accroche=(
                "Je retente seulement l'étape 7. Les six premières ne sont pas refaites, et "
                "je valide la sortie avant de continuer."
            ),
            points=[
                "Retries sur l'activity : les étapes 1 à 6 ne sont pas ré-exécutées.",
                "Validation de la sortie avec un schéma Pydantic.",
                "Si c'est invalide après les retries : branche d'escalade humaine.",
                "Les traces dans Studio permettent de diagnostiquer l'échec.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/building-workflows/activities/basics"),
            diagram=flow(["Étapes 1-6 (faites)", "Étape 7 échoue", "Retry", "Validation", "Suite"]),
        ),
    ],
)
