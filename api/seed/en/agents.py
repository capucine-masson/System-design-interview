"""English version of the Agents theme (same cards, same order as the French one)."""

from api.course_models import CardTranslation, ThemeTranslation

SOURCE = "LLM Powered Autonomous Agents (Lilian Weng, 2023)"

THEME = ThemeTranslation(
    slug="agents",
    titre="Agents",
    source_label=SOURCE,
    cards=[
        CardTranslation(
            titre="What is an LLM agent?",
            accroche=(
                "An agent is an LLM used as a controller: it decides which actions to "
                "take, calls tools and loops until the goal is reached."
            ),
            points=[
                "Three building blocks around the model: planning (decompose and revise), "
                "memory (short and long term), tools (APIs, code, search).",
                "Difference from a plain LLM call: the model itself chooses the sequence "
                "of steps, instead of following a chain written in advance.",
                "This brings flexibility, but also less predictability, more cost and more "
                "ways to fail.",
                "Examples: an assistant that searches and reads pages, a coding agent that "
                "runs the tests, a support agent that queries a CRM.",
            ],
            source_label=SOURCE,
            diagram_labels=["Planning", "LLM (controller)", "Memory", "Tools"],
        ),
        CardTranslation(
            titre="Planning and decomposition",
            accroche=(
                "For a complex task, the agent splits it into subtasks and handles them in order."
            ),
            points=[
                "Chain-of-thought: asking the model to think step by step gives a first "
                "form of plan.",
                "Tree of thoughts: explore several paths and evaluate which to pursue, "
                "useful when backtracking is needed.",
                "Full plan first or plan revised as you go: the second adapts to "
                "surprises, the first is more readable and economical.",
                "A planner / executor split lets you use a strong model to plan and a "
                "cheaper model to execute.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Reflection: ReAct and Reflexion",
            accroche=(
                "The agent alternates reflection and action, then learns from its "
                "mistakes by rereading them."
            ),
            points=[
                'ReAct interleaves "thought", "action" and "observation" steps: '
                "reasoning guides the tool, the tool result feeds the next step.",
                "Reflexion adds self-critique: when an attempt fails, the agent writes "
                "what did not work and keeps it in memory to try again.",
                "The failure signal must be reliable (a failing test, an API error); "
                "self-critique without an external signal corrects poorly.",
                "The number of attempts must be capped to avoid looping.",
            ],
            source_label=SOURCE,
            diagram_labels=["Thought", "Action (tool)", "Observation", "New thought"],
        ),
        CardTranslation(
            titre="Memory",
            accroche=(
                "An agent's memory works on two levels: the current context, which is "
                "limited, and an external store that can be queried."
            ),
            points=[
                "Short term: what fits in the context window (history, tool results); it "
                "is finite and costs tokens.",
                "Long term: an external store, often a vector database, queried by "
                "similarity to retrieve useful memories.",
                "Tactics to avoid saturating the context: summarize the history, keep "
                "only useful results, truncate tool outputs.",
                "Be careful what is memorized: wrong or sensitive data stored durably "
                "raises quality and confidentiality problems.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Tool use",
            accroche=(
                "Tools extend what the model can do reliably: exact calculation, "
                "up-to-date data, real actions."
            ),
            points=[
                "Function calling: each tool is described (name, role, JSON schema of the "
                "arguments) and the model produces a structured call.",
                "The quality of tool descriptions matters as much as that of the prompt: "
                "a vague name or description leads to bad calls.",
                "The code runs the tool and returns the result; it always validates the "
                "arguments, because the model's output is never reliable.",
                "Fewer, clearly distinct tools beat many overlapping tools.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="The control loop",
            accroche=(
                "At the heart of an agent is an observe, decide, act loop, which must be bounded."
            ),
            points=[
                "At each turn, the model sees the current state and chooses: call a tool "
                "or answer the user.",
                "A clear stopping criterion is needed: goal reached, maximum number of "
                "iterations, token or time budget exhausted.",
                "Detect loops: same actions repeated, no progress; in that case stop or "
                "hand over to a human.",
                "Everything is logged (full trace) so runs can be replayed and debugged.",
            ],
            source_label=SOURCE,
            diagram_labels=["State", "LLM decides", "Tool / answer"],
            edge_labels=["observation"],
        ),
        CardTranslation(
            titre="Guardrails and security",
            accroche=(
                "The more the agent can act, the more what it is allowed to do must be constrained."
            ),
            points=[
                "Least privilege: read-only tools by default, limited permissions, a "
                "sandbox to run code.",
                "Human confirmation before any irreversible action: deletion, payment, "
                "sending a message.",
                "Content fetched by tools (web pages, documents, emails) may contain "
                "malicious instructions: it is data, never orders (prompt injection).",
                "Argument validation, rate and cost limits, and an allow-list of actions "
                "rather than a deny-list.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Reliability: errors add up",
            accroche=(
                "Over several steps, small error rates multiply: an agent can fail often "
                "even if each step is good."
            ),
            points=[
                "Calculation to quote: 10 steps at 95% success each give about 60% overall "
                "success (0.95 to the power 10).",
                "So: reduce the number of steps, make each step more reliable, add checks "
                "between steps.",
                "LLM-specific limits add up: finite context, fragile long-term planning, "
                "sometimes invalid output format.",
                "Always plan a fallback path: retry, simplify, or escalate to a human.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Evaluating and observing an agent",
            accroche=(
                "We judge not only the final answer but the whole trajectory: tools "
                "chosen, arguments, number of steps."
            ),
            points=[
                "Log every thought, tool call and result to replay a run and find where "
                "it went off the rails.",
                "Measure the task success rate, but also the number of steps, latency and "
                "cost per task.",
                "Evaluate tool choice and argument extraction separately: these are "
                "frequent, easy-to-test failures.",
                "Feed the test set with the real failures met in production.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Agent or workflow?",
            accroche=(
                "Before building an agent, I ask whether a fixed sequence of steps would "
                "not be enough."
            ),
            points=[
                "Workflow: the steps are written in advance, the LLM fills in each one; "
                "predictable, testable, cheaper.",
                "Agent: the model chooses the steps; suited to open-ended tasks whose path "
                "cannot be predicted.",
                "Practical rule: start with the simplest approach (one call), then a "
                "workflow, and add autonomy only if the need has been measured.",
                "In an interview: explaining this flexibility versus control trade-off "
                "shows good engineering judgment.",
            ],
            source_label=SOURCE,
        ),
    ],
)
