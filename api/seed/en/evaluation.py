"""English version of the LLM evaluation theme (same cards, same order as the French one)."""

from api.course_models import CardTranslation, ThemeTranslation

SOURCE = "AI Evals FAQ (Hamel Husain)"

THEME = ThemeTranslation(
    slug="evaluation",
    titre="LLM evaluation",
    source_label=SOURCE,
    cards=[
        CardTranslation(
            titre="What evals are for",
            accroche=(
                "An eval is a test that checks the product does what users and the "
                "business expect, not just that the model is good."
            ),
            points=[
                "Distinguish public benchmarks, which compare models, from product evals, "
                "which measure MY use case.",
                "They are used to decide: change model, prompt or chunking while knowing "
                "whether we are improving or regressing.",
                "They are part of development, like debugging, not a separate workstream "
                "to schedule later.",
                "Without evals, changes are made by gut feeling and regressions are "
                "discovered by users.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Start with error analysis",
            accroche=("Before writing any metric, I read real traces and note what goes wrong."),
            points=[
                "Step 1: reread a few dozen traces and take free-form notes on every "
                "defect observed.",
                "Step 2: group these notes into failure categories, then count how many "
                "times each category appears.",
                "Fix the most frequent or most serious categories first, instead of "
                "guessing where the problem is.",
                "Redo this analysis after every major change, with new traces (aim: about "
                "a hundred per cycle).",
            ],
            source_label=SOURCE,
            diagram_labels=["Real traces", "Free notes", "Failure categories", "Counting", "Fix"],
        ),
        CardTranslation(
            titre="Building a test set",
            accroche=(
                "The test set is a representative sample of real inputs, completed if "
                "needed with well-structured synthetic cases."
            ),
            points=[
                "Ideal: real traces, randomly sampled, then completed with rare or "
                "atypical cases spotted separately.",
                "To start without data, generate synthetic cases, but vary explicit "
                "dimensions (user type, intent, difficulty).",
                "Be careful with synthetic data for specialized or high-stakes domains: it "
                "often lacks the real mess of users.",
                "Version the set, and keep a part untouched (test) that is never used to "
                "tune the system.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Code-based checks first",
            accroche=("When a rule is enough to detect a defect, I write code, not an LLM judge."),
            points=[
                "Examples: valid JSON, required fields, maximum length, date format, "
                "absence of a banned word.",
                "These assertions are free, deterministic and fast: they run on every commit.",
                "For generated code, run the tests; for an extraction, compare with the "
                "expected field.",
                "The LLM judge is reserved for what needs judgment: tone, relevance, "
                "faithfulness to a source.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="LLM-as-judge",
            accroche=(
                "An LLM judge automatically scores outputs on a precise criterion, "
                "provided it is framed and validated."
            ),
            points=[
                'One judge per failure mode (for example "does it cite a non-existent '
                'source?"), not a single judge for "overall quality".',
                "Binary output (pass/fail) plus a short justification: much more stable "
                "than 1-to-5 scores.",
                "The prompt contains the definition of the criterion, positive and "
                "negative examples, and only the necessary context.",
                "Start with a powerful model, then test a cheaper model against the same "
                "human labels.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Validating the judge",
            accroche=(
                "A judge is only reliable if it is measured against human labels, like "
                "any classifier."
            ),
            points=[
                "Have a human label a sample, then split it into train (prompt examples), "
                "dev (tuning) and test (final verdict).",
                "Measure the true positive rate (failures correctly caught) and the true "
                "negative rate (no false alarms), not just overall accuracy.",
                "When they disagree, read the cases first: often the instruction is vague "
                "or the human label is debatable.",
                "The judge's test set stays untouched until the end to avoid fooling yourself.",
            ],
            source_label=SOURCE,
            diagram_labels=["Human labels", "Judge prompt", "TPR / TNR on dev"],
            edge_labels=["tunes"],
        ),
        CardTranslation(
            titre="Binary rather than scores, and generic metrics",
            accroche=("I favor pass/fail verdicts on precise criteria rather than general scores."),
            points=[
                "1-to-5 scales are poorly calibrated: two annotators do not agree on the "
                "difference between a 3 and a 4.",
                "Aggregate with an overall pass rate, then break it down by criterion or "
                "topic to know what to fix.",
                'Generic scores ("helpfulness", BERTScore, ROUGE) measure product quality '
                "poorly: good for spotting traces to read, not for deciding.",
                "For document retrieval, similarity or ranking metrics are on the other "
                "hand relevant.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Human annotation",
            accroche=(
                "Humans remain the reference: annotation must be organized to be fast and "
                "consistent."
            ),
            points=[
                "Name a domain expert as the referee of quality decisions; add annotators "
                "only if necessary, measuring their agreement.",
                "Make reviewing easy: show the context and intermediate steps, use "
                "keyboard shortcuts, show progress.",
                "A notebook or a small home-made interface is enough to start.",
                "Error analysis stays in-house: outsourcing it loses the understanding of "
                "the product.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Evaluating a RAG or an agent",
            accroche=(
                "For a multi-step system, I evaluate each step separately before the final result."
            ),
            points=[
                "RAG: on one side retrieval (did we find the right passages?), on the "
                "other generation (does the answer rely on them?).",
                "For retrieval, use classic ranking metrics: recall@k, MRR.",
                "Agent or multi-turn conversation: find at which step the trajectory goes "
                "astray, and evaluate the handoff to a human.",
                "This tells you whether to improve retrieval, the prompt, the tool choice "
                "or the model.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Continuous evals: CI and production",
            accroche=(
                "Evals act as a safety net on every change, then as monitoring in production."
            ),
            points=[
                "In CI: a fast regression set (assertions and a few judges) that runs on "
                "every prompt or model change.",
                "In production: sample real traces, evaluate them, and feed the test set "
                "with the new failures.",
                "Do not confuse guardrails, which block an output in real time, with "
                "evaluators, which measure quality, often after the fact.",
                "For stakeholders: tell what changed and why, rather than showing a "
                "generic dashboard.",
            ],
            source_label=SOURCE,
        ),
    ],
)
