"""English version of the prompt engineering theme (same cards, same order as the French)."""

from api.course_models import CardTranslation, ThemeTranslation

SOURCE = "Prompt Engineering (Lilian Weng, 2023)"

THEME = ThemeTranslation(
    slug="prompt-engineering",
    titre="Prompt engineering",
    source_label=SOURCE,
    cards=[
        CardTranslation(
            titre="Structuring a good prompt",
            accroche=(
                "A good prompt is a specification: it states the task, the context, the "
                "expected format and what is forbidden."
            ),
            points=[
                "Useful elements: the role or target audience, the precise task, the "
                "constraints, the output format, one or two examples.",
                'Be explicit rather than leave it to guesswork: "answer in 3 bullets of '
                'fewer than 20 words" beats "be concise".',
                "Delimit external content (tags, quotes) to separate instructions from "
                "data, which also reduces prompt injection.",
                "A prompt is tested like code: change one thing at a time and compare on a "
                "set of examples.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Zero-shot and few-shot",
            accroche=(
                "In zero-shot you only describe the task; in few-shot you add a few "
                "input-output examples to the prompt."
            ),
            points=[
                "Few-shot teaches format and style by example, without retraining the "
                "model: it is in-context learning.",
                "It helps mostly when the instruction alone is ambiguous or the format "
                "unusual; on recent models zero-shot is often enough.",
                "Cost: each example consumes tokens on every call, hence latency and money.",
                "A few examples (3 to 5) are usually enough; beyond that the gain drops quickly.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Choosing and ordering examples",
            accroche=(
                "Few-shot results depend a lot on which examples are used and in what order."
            ),
            points=[
                "Choosing examples close to the question (embedding similarity search) "
                "often gives better results than fixed examples.",
                "Known biases: the model favors the majority label among the examples and "
                "the one that appears last.",
                "Countermeasures: balance the classes, vary the order, cover varied cases "
                "rather than near-identical examples.",
                "Choose on a measured development set, not by intuition.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Instructions and instruct models",
            accroche=(
                '"Instruct" models are trained to follow instructions; write them as you '
                "would for a competent colleague who has no context."
            ),
            points=[
                "Describe the audience and the goal: explaining what the output will be "
                "used for improves the level of detail.",
                "Prefer saying what to do rather than what to avoid, and give the success "
                "criteria.",
                "Separate the system prompt (stable rules) from the user message (variable data).",
                "For machine output, ask for a structured format and validate it "
                "afterwards, because the output is never guaranteed.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Chain-of-thought",
            accroche=(
                "Asking the model to reason step by step before answering often improves "
                "logic and calculation tasks."
            ),
            points=[
                "Few-shot version: the examples show the full reasoning before the "
                'answer; zero-shot version: a simple instruction like "think step by step".',
                "The gain is clear on arithmetic, logic and multi-hop reasoning, "
                "especially with large enough models.",
                "Cost: more generated tokens, hence more latency and money, and the "
                "displayed reasoning is not always faithful.",
                'Recent "reasoning" models do this work internally: no need to ask for it '
                "explicitly.",
            ],
            source_label=SOURCE,
            diagram_labels=["Question", "Reasoning steps", "Final answer"],
        ),
        CardTranslation(
            titre="Self-consistency",
            accroche=(
                "Several independent reasoning chains are generated and the most frequent "
                "answer is kept."
            ),
            points=[
                "Sample N chains of thought with a temperature > 0, then take a majority "
                "vote on the final answer.",
                "Intuition: errors are scattered, the right answer comes back more often.",
                "Real gain on calculation and reasoning, but the cost is multiplied by N "
                "(for example 5 to 10 calls).",
                "Reserve it for cases where an error is costly and the answer is short "
                "and comparable (a number, a class).",
            ],
            source_label=SOURCE,
            diagram_labels=["Question", "Chain 1", "Chain 2", "Chain N", "Majority vote"],
        ),
        CardTranslation(
            titre="Tree of Thoughts",
            accroche=(
                "Instead of a single chain, the model explores several paths as a tree "
                "and evaluates each step."
            ),
            points=[
                'At each step, the model proposes several possible "thoughts", then '
                "scores them (promising or not).",
                "A search algorithm (breadth-first or depth-first) chooses which branches "
                "to expand or abandon.",
                "Useful for problems that require looking ahead or backtracking (puzzles, "
                "planning).",
                "Very expensive in calls: reserved for hard tasks where a simple chain fails.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Automatic prompt optimization",
            accroche=(
                "An LLM can be used to propose, test and improve prompts, provided there "
                "is a measure."
            ),
            points=[
                "Principle: a model generates instruction variants, they are evaluated on "
                "a set of examples, the best is kept and the loop restarts.",
                "Approaches like APE automate this loop; the idea is to treat the prompt "
                "as a parameter to optimize.",
                "Without a reliable metric, optimization overfits or drifts: evals come "
                "before automation.",
                "Keep a separate test set to check that the gain is real.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Prompt, tools and external knowledge",
            accroche=(
                "The prompt alone only knows what the model has learned: for the rest, "
                "give it context or tools."
            ),
            points=[
                "Retrieval: inject relevant passages into the prompt to answer with "
                "up-to-date or private information.",
                "Tools: calculator, code interpreter, APIs, called by the model when it "
                "needs them, for what it does badly (exact calculation).",
                "Structured output: ask for JSON that matches a schema, then validate it in code.",
                "Any external content is untrusted data: never instructions to execute.",
            ],
            source_label=SOURCE,
        ),
    ],
)
