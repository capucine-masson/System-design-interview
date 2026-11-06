"""Catégorie Agents et IA : où appeler le LLM, Agent, Runner, pièges."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow
from api.seed.workflows.common import SOURCE, doc

AGENTS_PAGE = doc("/studio/workflows/building-workflows/durable_agents")

THEME = ThemeContent(
    slug="agents",
    titre="Agents et IA",
    source_label=SOURCE,
    source_url=AGENTS_PAGE,
    cards=[
        CardContent(
            titre="Où appeler le LLM ?",
            essentielle=True,
            accroche=(
                "Dans une activity, ou via le plugin Mistral. Jamais directement dans le "
                "workflow, qui doit rester déterministe."
            ),
            points=[
                "Un appel LLM est un effet de bord, et sa réponse varie.",
                "Dans une activity : résultat stocké, pas de nouvel appel au replay.",
                "Ou via le plugin Mistral, qui fournit Agent et Runner.",
                "Dans le workflow lui-même : interdit, le replay donnerait un autre plan.",
            ],
            source_label=SOURCE,
            source_url=AGENTS_PAGE,
            diagram=flow(["Workflow (plan)", "Activity", "Appel LLM", "Résultat stocké"]),
        ),
        CardContent(
            titre="Agent et Runner",
            accroche=(
                "Agent décrit le LLM (modèle, instructions, outils). Runner l'exécute et gère "
                "la boucle de conversation."
            ),
            points=[
                "Agent(...) : modèle, instructions, outils et handoffs.",
                "Runner.run(...) : exécute l'agent avec les entrées de l'utilisateur.",
                "Le plugin s'installe avec mistralai-workflows[mistralai].",
                "Le tout tourne dans un workflow durable : reprise possible après crash.",
            ],
            source_label=SOURCE,
            source_url=AGENTS_PAGE,
        ),
        CardContent(
            titre="Handoffs, outils intégrés et MCP",
            accroche=(
                "Un agent peut passer la main à un autre agent, utiliser des outils et se "
                "connecter à des serveurs MCP."
            ),
            points=[
                "Handoff : déléguer une tâche à un agent spécialisé.",
                "MCP : se connecter à des serveurs d'outils via le Model Context Protocol.",
                "Le plugin gère les configs MCP en stdio et en SSE.",
                "Une activity peut aussi servir d'outil à l'agent.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/building-workflows/plugins"),
        ),
        CardContent(
            titre="Durable agents : bientôt dépréciés",
            essentielle=True,
            accroche=(
                "La doc annonce que les durable agents vont être dépréciés. Mistral "
                "recommande son Agents SDK pour les nouveaux agents."
            ),
            points=[
                "Formulation de la doc : « about to be deprecated » : pas encore effectif.",
                "Pour un nouveau projet, partir sur l'Agents SDK.",
                "Avec RemoteSession, c'est le Mistral Agents SDK qui sert la production.",
            ],
            source_label=SOURCE,
            source_url=AGENTS_PAGE,
        ),
        CardContent(
            titre="Piège RemoteSession : agents orphelins",
            accroche=(
                "Avec RemoteSession, sans identifiant fixe, chaque exécution crée un nouvel "
                "agent côté Mistral, qui reste orphelin."
            ),
            points=[
                "Sans id fixe, chaque exécution du workflow crée un agent distant.",
                "Ces agents s'accumulent sans être réutilisés.",
                "Solution : donner un identifiant stable à l'agent.",
            ],
            source_label=SOURCE,
            source_url=AGENTS_PAGE,
        ),
        CardContent(
            titre="Secrets : jamais dans les inputs d'activity",
            essentielle=True,
            accroche=(
                "Les entrées d'une activity sont enregistrées dans l'historique. Y mettre un "
                "secret, c'est le stocker en clair dans la trace."
            ),
            points=[
                "Les inputs et outputs d'activity sont persistés dans l'historique.",
                "Un mot de passe ou une clé API passés en argument y seraient visibles.",
                "Bonne pratique : lire le secret dans l'activity, via la gestion des secrets.",
                "Le chiffrement des payloads protège, mais ne remplace pas cette règle.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/building-workflows/encryption"),
        ),
    ],
)
