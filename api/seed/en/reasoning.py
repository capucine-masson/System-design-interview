"""English version of the reasoning / thinking theme (same cards, same order as the French)."""

from api.course_models import CardTranslation, ThemeTranslation

SOURCE = '"Why We Think" (Lilian Weng, 2025)'

THEME = ThemeTranslation(
    slug="reasoning",
    titre='Reasoning and "thinking"',
    source_label=SOURCE,
    cards=[
        CardTranslation(
            titre="Why let the model think",
            accroche=(
                "Giving the model time to think means giving it more compute on the "
                "question, like a human who takes the time to reason."
            ),
            points=[
                "Analogy: fast thinking (intuition) versus slow thinking (explicit "
                "reasoning); a classic LLM answers in a single pass.",
                "Writing intermediate steps adds tokens, hence compute, before the final answer.",
                "Compute can adapt to difficulty: little thinking for a simple question, "
                "a lot for a math problem.",
                "The price: more latency and more billed tokens per request.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Test-time compute",
            accroche=(
                "Test-time compute means spending compute at inference to improve the "
                "answer, instead of making the model bigger."
            ),
            points=[
                "Two levers to improve a model: more compute at training, or more compute "
                "at each question.",
                "Main forms: generate a long reasoning chain, sample several answers, or "
                "revise one's answer.",
                "A smaller model that thinks for a long time can match a bigger one on "
                "some tasks, with the cost moved to inference.",
                "The gain has diminishing returns and depends on the task: strong on math "
                "and code, weak on factual recall.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Chain of thought as intermediate computation",
            accroche=(
                "Reasoning tokens act as working memory: the model writes in order to "
                "compute better."
            ),
            points=[
                "A transformer has a fixed depth: writing steps lets it perform more "
                "sequential operations than in a single pass.",
                "The benefit is stronger with large models.",
                "More thinking tokens improve accuracy up to a plateau, beyond which you "
                "pay without gaining.",
                "A thinking budget can be set to control cost and latency.",
            ],
            source_label=SOURCE,
            diagram_labels=["Question", "Thinking tokens", "Answer"],
        ),
        CardTranslation(
            titre="Parallel sampling",
            accroche="Several candidate answers are generated, then one is chosen.",
            points=[
                "Best-of-N: draw N answers and keep the one a verifier judges best (tests, "
                "reward model).",
                "Majority vote (self-consistency): keep the most frequent answer, useful "
                "when the final answer is short and comparable.",
                "Beam search: keep several partial paths and drop the least promising.",
                "Easy to parallelize and needs no change to the model, but cost grows "
                "linearly with N.",
            ],
            source_label=SOURCE,
            diagram_labels=["Question", "Answer 1", "Answer 2", "Answer N", "Verifier / vote"],
        ),
        CardTranslation(
            titre="Sequential revision",
            accroche=(
                "The model rereads its answer and corrects it; it only works if it gets "
                "real feedback."
            ),
            points=[
                "Principle: answer, critique, new answer, possibly repeated several times.",
                "Without external feedback, self-correction is unreliable: the model can "
                "even spoil an answer that was already correct.",
                "With a reliable signal (unit tests, a tool result, an error message), "
                "correction becomes effective.",
                "Rule: first look for an external verifier, only then ask the model to "
                "correct itself.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Reinforcement learning for reasoning",
            accroche=(
                "The model is trained with a reward when its final answer is correct, and "
                "learns by itself to reason for longer."
            ),
            points=[
                "Ideal domains: those where the answer is automatically verifiable, like "
                "math (exact answer) and code (passing tests).",
                "DeepSeek-R1 is the reference example, trained with a GRPO-type algorithm "
                "and simple rewards on these tasks.",
                "Behaviors emerge: checking itself, trying another approach, extending the "
                "thinking on hard problems.",
                "Limit: outside verifiable domains (writing, judgment), the reward is "
                "harder to define.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Process reward or outcome reward",
            accroche=("You can reward only the final answer, or score each step of the reasoning."),
            points=[
                "Outcome reward: simple, judges the final answer; the signal is sparse but "
                "hard to fool.",
                "Process reward: a model scores each step, useful to guide a search and "
                "spot the exact error.",
                'But defining a "good step" is hard, and reward models can be exploited '
                "(reward hacking).",
                "For this reason, several recent works prefer verifiable outcome rewards.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Faithfulness of displayed reasoning",
            accroche=(
                "The displayed chain of thought is not always the real reason for the "
                "model's answer."
            ),
            points=[
                "Experiments show the model can be influenced by a hint without "
                "mentioning it in its reasoning.",
                "Reasoning models acknowledge such influences more often than classic "
                "models, without any guarantee.",
                "Reading the chain of thought helps monitor a model, but it is not proof "
                "of what it is really doing.",
                "Penalizing bad reasoning too directly can push the model to hide it "
                "rather than correct itself.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Tools for better reasoning",
            accroche=(
                "For calculations and facts, the model does better by delegating to a "
                "tool than by guessing."
            ),
            points=[
                "Code interpreter: the model writes a program and it is executed (PAL-type "
                "approach), for an exact result.",
                "Search and APIs: ReAct alternates reasoning and tool calls to fetch "
                "up-to-date information.",
                "Recent reasoning models can call tools in the middle of their thinking.",
                "The tool result also serves as reliable external feedback to correct a reasoning.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="When to pay for thinking?",
            accroche=(
                "A model that thinks costs more and answers more slowly: I reserve it for "
                "the tasks that benefit."
            ),
            points=[
                "Turn on: math, code, planning, multi-step analyses, cases where an error "
                "is costly.",
                "Avoid: simple classification, extraction, short answers and "
                "low-latency chat, where quality does not move.",
                "Measure: compare quality, latency and cost with and without thinking on "
                "your own evaluation set.",
                "Tune the thinking budget to difficulty, or even route easy requests to a "
                "simpler model.",
            ],
            source_label=SOURCE,
        ),
    ],
)
