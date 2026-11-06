"""English version of the CI/CD and infrastructure theme (same cards, same order as the French)."""

from api.course_models import CardTranslation, ThemeTranslation

ACTIONS = "Understanding GitHub Actions (GitHub Docs)"
K8S = "Kubernetes Tutorial for Beginners (Spacelift)"
TERRAFORM = "What is Terraform? (Spacelift)"
TEMPORAL = "Understanding Temporal (Temporal Docs)"

THEME = ThemeTranslation(
    slug="cicd-infra",
    titre="CI/CD and infrastructure",
    source_label="Sources listed on each card",
    cards=[
        CardTranslation(
            titre="GitHub Actions: workflow, event, job",
            accroche=(
                "GitHub Actions automatically runs build, tests and deployment on every "
                "repository event (push, pull request, schedule)."
            ),
            points=[
                "A workflow is a YAML file in .github/workflows; it triggers on an event "
                "(push, pull_request, schedule) or manually.",
                "It contains jobs, which run in parallel by default; needs creates a "
                "dependency between two jobs.",
                "Each job contains steps run in order on the same runner: a shell command or "
                "an action.",
                "Example to quote: on every pull request, run ruff, mypy and pytest, and "
                "block the merge if one fails.",
            ],
            source_label=ACTIONS,
            diagram_labels=["Event (push)", "Workflow", "Jobs", "Steps"],
        ),
        CardTranslation(
            titre="GitHub Actions: runners, actions and matrix",
            accroche=(
                "A runner is the machine that runs a job; an action is a reusable building "
                "block; a matrix repeats a job over several variants."
            ),
            points=[
                "GitHub-hosted runners: Ubuntu, Windows, macOS, with a fresh machine on every "
                "run; you can also host your own runners.",
                "A ready-made action (check out the code, install Python) is reused through "
                "the Marketplace; you can write your own.",
                "A matrix runs the same job for several Python versions or systems, without "
                "copy-paste.",
                "A workflow can call another one to share steps.",
            ],
            source_label=ACTIONS,
        ),
        CardTranslation(
            titre="Kubernetes: orchestrating containers",
            accroche=(
                "Kubernetes starts, restarts, spreads and scales containerized applications "
                "across a group of machines."
            ),
            points=[
                "A cluster = nodes (machines or VMs) that run the applications, and a "
                "control plane that decides what runs where.",
                "The control plane holds kube-apiserver (entry point), kube-scheduler "
                "(placement) and kube-controller-manager; each node has a kubelet.",
                "Core idea: you declare the desired state ('3 copies of this image') and "
                "Kubernetes fixes the gap with reality on its own.",
                "Open source project originally from Google, maintained by the CNCF.",
            ],
            source_label=K8S,
            diagram_labels=["Control plane", "Node 1", "Node 2"],
        ),
        CardTranslation(
            titre="Kubernetes: Pod, Deployment and Service",
            accroche=(
                "Three objects to know: the Pod runs the containers, the Deployment keeps "
                "the right number of them, the Service makes them reachable."
            ),
            points=[
                "Pod: the smallest unit, one or more containers sharing a network; it is "
                "ephemeral.",
                "Deployment: manages a ReplicaSet of identical Pods, replaces those that "
                "fall and allows updates and rollbacks.",
                "Service: a stable address in front of Pods that change; Ingress then "
                "exposes the Service over HTTP from outside.",
                "Other objects: Namespace, ConfigMap and Secret (configuration), Job and "
                "CronJob, HorizontalPodAutoscaler.",
            ],
            source_label=K8S,
            diagram_labels=["Deployment", "ReplicaSet", "Pods", "Service"],
        ),
        CardTranslation(
            titre="Kubernetes: manifests and kubectl",
            accroche=(
                "You describe objects in YAML files (manifests) and apply them with kubectl."
            ),
            points=[
                "A manifest contains apiVersion, kind (Pod, Deployment...), metadata and "
                "spec; kubectl apply -f file.yaml creates or updates it.",
                "Common commands: kubectl get pods, kubectl scale deployment nginx "
                "--replicas 5, kubectl port-forward service/nginx 8080:80.",
                "Good practice: keep manifests in Git and use apply (or a GitOps tool) "
                "rather than imperative commands in production.",
                "To try it locally, K3s is a lightweight, easy-to-install version.",
            ],
            source_label=K8S,
        ),
        CardTranslation(
            titre="Terraform: infrastructure as code",
            accroche=(
                "Terraform describes infrastructure (servers, networks, databases) in files, "
                "compares it with reality, then applies the difference."
            ),
            points=[
                "Declarative language HCL: you write the desired state, not the steps to "
                "reach it.",
                "Cycle: terraform init, validate, plan (shows what will be created, changed "
                "or deleted), apply (executes), destroy (removes).",
                "Provider = plugin that talks to an API (AWS, Azure, GCP...); resource = a "
                "managed object (VM, bucket, network).",
                "Benefit: infrastructure is versioned, reviewed in pull requests and "
                "reproducible.",
            ],
            source_label=TERRAFORM,
            diagram_labels=["HCL code", "plan", "apply", "Infrastructure"],
        ),
        CardTranslation(
            titre="Terraform: state, modules and good practices",
            accroche=(
                "Terraform remembers what it manages in a state file; modules and remote "
                "state make teamwork safe."
            ),
            points=[
                "The state (terraform.tfstate) links the code to the real objects; it can "
                "contain secrets, so do not commit it.",
                "In a team, use a remote, locked state (e.g. an S3 bucket with locking) to "
                "avoid two simultaneous applies.",
                "A module groups reusable resources; the main folder is the root module.",
                "Always review the plan before apply. Since 2023 the license is BSL; "
                "OpenTofu is the open source fork.",
            ],
            source_label=TERRAFORM,
        ),
        CardTranslation(
            titre="Temporal: durable execution",
            accroche=(
                "Temporal guarantees that a long business process runs to completion, even "
                "if a server crashes along the way."
            ),
            points=[
                "A workflow is code (loops, conditions) that orchestrates a process; it must "
                "be deterministic so it can be replayed.",
                "Calls to the outside world (API, database, email) go in activities, with a "
                "retry policy and timeouts configured.",
                "Temporal records each step in an event history; after a crash, another "
                "process replays the history and resumes where things stood.",
                "Example to quote: payment, booking then confirmation email, without ever "
                "charging twice.",
            ],
            source_label=TEMPORAL,
        ),
        CardTranslation(
            titre="Temporal: worker, task queue and service",
            accroche=(
                "Your code runs at your side in workers; the Temporal Service keeps the "
                "history and hands out work through queues."
            ),
            points=[
                "Worker: the process that runs your workflows and activities, deployed on "
                "your infrastructure.",
                "It polls a task queue to fetch work: nothing is pushed to it, so you add "
                "workers to scale.",
                "Temporal Service: the backend (with PostgreSQL, MySQL or Cassandra "
                "persistence); it never runs your code itself.",
                "Tools: Temporal UI, CLI; temporal server start-dev starts a local "
                "environment.",
            ],
            source_label=TEMPORAL,
            diagram_labels=["Worker", "Task queue", "Temporal Service"],
            edge_labels=["polls"],
        ),
    ],
)
