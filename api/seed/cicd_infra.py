"""Contenu du thème CI/CD et infrastructure (texte original, à dire à l'oral)."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph

ACTIONS = "Understanding GitHub Actions (GitHub Docs)"
ACTIONS_URL = "https://docs.github.com/en/actions/get-started/understand-github-actions"
K8S = "Kubernetes Tutorial for Beginners (Spacelift)"
K8S_URL = "https://spacelift.io/blog/kubernetes-tutorial"
TERRAFORM = "What is Terraform? (Spacelift)"
TERRAFORM_URL = "https://spacelift.io/blog/what-is-terraform"
TEMPORAL = "Understanding Temporal (Temporal Docs)"
TEMPORAL_URL = "https://docs.temporal.io/evaluate/understanding-temporal"

THEME = ThemeContent(
    slug="cicd-infra",
    titre="CI/CD et infrastructure",
    source_label="Sources indiquées sur chaque carte",
    source_url=None,
    cards=[
        CardContent(
            titre="GitHub Actions : workflow, événement, job",
            essentielle=True,
            accroche=(
                "GitHub Actions exécute automatiquement build, tests et déploiement à chaque "
                "événement du dépôt (push, pull request, planning)."
            ),
            points=[
                "Un workflow est un fichier YAML dans .github/workflows ; il se déclenche sur "
                "un événement (push, pull_request, schedule) ou à la main.",
                "Il contient des jobs, qui tournent en parallèle par défaut ; needs crée "
                "une dépendance entre deux jobs.",
                "Chaque job contient des steps exécutés dans l'ordre sur le même runner : "
                "une commande shell ou une action.",
                "Exemple à citer : à chaque pull request, lancer ruff, mypy et pytest, et "
                "bloquer la fusion si l'un échoue.",
            ],
            source_label=ACTIONS,
            source_url=ACTIONS_URL,
            diagram=flow(["Événement (push)", "Workflow", "Jobs", "Steps"]),
        ),
        CardContent(
            titre="GitHub Actions : runners, actions et matrix",
            accroche=(
                "Un runner est la machine qui exécute un job ; une action est une brique "
                "réutilisable ; une matrix répète un job sur plusieurs variantes."
            ),
            points=[
                "Runners hébergés par GitHub : Ubuntu, Windows, macOS, avec une machine "
                "neuve à chaque exécution ; on peut aussi héberger ses propres runners.",
                "Une action prête à l'emploi (récupérer le code, installer Python) se "
                "réutilise via le Marketplace ; on peut écrire la sienne.",
                "Une matrix lance le même job pour plusieurs versions de Python ou plusieurs "
                "systèmes, sans copier-coller.",
                "Un workflow peut en appeler un autre pour mutualiser des étapes.",
            ],
            source_label=ACTIONS,
            source_url=ACTIONS_URL,
        ),
        CardContent(
            titre="Kubernetes : orchestrer des conteneurs",
            essentielle=True,
            accroche=(
                "Kubernetes lance, redémarre, répartit et fait grandir des applications "
                "conteneurisées sur un groupe de machines."
            ),
            points=[
                "Un cluster = des nodes (machines ou VM) qui exécutent les applications, et "
                "un control plane qui décide quoi lancer où.",
                "Le control plane contient kube-apiserver (point d'entrée), "
                "kube-scheduler (placement) et kube-controller-manager ; chaque node "
                "a un kubelet.",
                "Idée centrale : on déclare l'état voulu (« 3 copies de cette image ») et "
                "Kubernetes répare tout seul l'écart avec la réalité.",
                "Projet open source d'origine Google, maintenu par la CNCF.",
            ],
            source_label=K8S,
            source_url=K8S_URL,
            diagram=graph(
                [
                    ("cp", "Control plane", 0, 1),
                    ("n1", "Node 1", 1, 0),
                    ("n2", "Node 2", 1, 2),
                ],
                [("cp", "n1"), ("cp", "n2")],
            ),
        ),
        CardContent(
            titre="Kubernetes : Pod, Deployment et Service",
            essentielle=True,
            accroche=(
                "Trois objets à connaître : le Pod fait tourner les conteneurs, le "
                "Deployment en garde le bon nombre, le Service les rend joignables."
            ),
            points=[
                "Pod : la plus petite unité, un ou plusieurs conteneurs qui partagent le "
                "réseau ; il est éphémère.",
                "Deployment : gère un ReplicaSet de Pods identiques, remplace ceux qui "
                "tombent et permet les mises à jour et retours arrière (rollback).",
                "Service : adresse stable devant des Pods qui changent ; Ingress expose "
                "ensuite le Service sur HTTP depuis l'extérieur.",
                "Autres objets : Namespace, ConfigMap et Secret (configuration), Job et "
                "CronJob, HorizontalPodAutoscaler.",
            ],
            source_label=K8S,
            source_url=K8S_URL,
            diagram=flow(["Deployment", "ReplicaSet", "Pods", "Service"]),
        ),
        CardContent(
            titre="Kubernetes : manifests et kubectl",
            accroche=(
                "On décrit les objets dans des fichiers YAML (manifests) et on les applique "
                "avec kubectl."
            ),
            points=[
                "Un manifest contient apiVersion, kind (Pod, Deployment...), metadata et "
                "spec ; kubectl apply -f fichier.yaml le crée ou le met à jour.",
                "Commandes courantes : kubectl get pods, kubectl scale deployment nginx "
                "--replicas 5, kubectl port-forward service/nginx 8080:80.",
                "Bonne pratique : garder les manifests dans Git et utiliser apply (ou un "
                "outil GitOps) plutôt que des commandes impératives en production.",
                "Pour essayer en local, K3s est une version légère d'installation facile.",
            ],
            source_label=K8S,
            source_url=K8S_URL,
        ),
        CardContent(
            titre="Terraform : l'infrastructure comme code",
            essentielle=True,
            accroche=(
                "Terraform décrit l'infrastructure (serveurs, réseaux, bases) dans des "
                "fichiers, compare avec la réalité, puis applique la différence."
            ),
            points=[
                "Langage déclaratif HCL : on écrit l'état voulu, pas les étapes pour y "
                "arriver.",
                "Cycle : terraform init, validate, plan (montre ce qui sera créé, modifié ou "
                "supprimé), apply (exécute), destroy (supprime).",
                "Provider = plugin qui parle à une API (AWS, Azure, GCP...) ; "
                "resource = un objet géré (VM, bucket, réseau).",
                "Avantage : l'infrastructure est versionnée, relue en pull request et "
                "reproductible.",
            ],
            source_label=TERRAFORM,
            source_url=TERRAFORM_URL,
            diagram=flow(["Code HCL", "plan", "apply", "Infrastructure"]),
        ),
        CardContent(
            titre="Terraform : state, modules et bonnes pratiques",
            accroche=(
                "Terraform retient ce qu'il gère dans un fichier d'état ; modules et état "
                "distant rendent le travail en équipe sûr."
            ),
            points=[
                "Le state (terraform.tfstate) fait le lien entre le code et les objets "
                "réels ; il peut contenir des secrets, donc ne pas le committer.",
                "En équipe, utiliser un state distant et verrouillé (ex. bucket S3 avec "
                "verrou) pour éviter deux apply simultanés.",
                "Un module regroupe des ressources réutilisables ; le dossier principal est "
                "le root module.",
                "Toujours relire le plan avant apply. Depuis 2023 la licence est BSL ; "
                "OpenTofu en est le fork open source.",
            ],
            source_label=TERRAFORM,
            source_url=TERRAFORM_URL,
        ),
        CardContent(
            titre="Temporal : exécution durable",
            accroche=(
                "Temporal garantit qu'un processus métier long va jusqu'au bout, même si "
                "un serveur plante en cours de route."
            ),
            points=[
                "Un workflow est du code (boucles, conditions) qui orchestre un processus ; "
                "il doit être déterministe pour pouvoir être rejoué.",
                "Les appels au monde extérieur (API, base, e-mail) se font dans des "
                "activities, avec politique de nouvelle tentative et timeouts configurés.",
                "Temporal enregistre chaque étape dans un historique d'événements ; après "
                "un crash, un autre processus rejoue l'historique et reprend où l'on en était.",
                "Exemple à citer : paiement, réservation puis e-mail de confirmation, sans "
                "jamais débiter deux fois.",
            ],
            source_label=TEMPORAL,
            source_url=TEMPORAL_URL,
        ),
        CardContent(
            titre="Temporal : worker, task queue et service",
            accroche=(
                "Le code tourne chez vous dans des workers ; le Temporal Service tient "
                "l'historique et distribue le travail via des files."
            ),
            points=[
                "Worker : processus qui exécute vos workflows et activities, déployé sur "
                "votre infrastructure.",
                "Il interroge une task queue pour récupérer du travail : rien ne lui est "
                "poussé, donc on ajoute des workers pour monter en charge.",
                "Temporal Service : le backend (avec persistance PostgreSQL, MySQL ou "
                "Cassandra) ; il ne lance jamais votre code lui-même.",
                "Outils : Temporal UI, CLI ; temporal server start-dev lance un "
                "environnement local.",
            ],
            source_label=TEMPORAL,
            source_url=TEMPORAL_URL,
            diagram=graph(
                [
                    ("w", "Worker", 0, 0),
                    ("q", "Task queue", 1, 0),
                    ("s", "Temporal Service", 2, 0),
                ],
                [("w", "q", "interroge"), ("q", "s")],
            ),
        ),
    ],
)
