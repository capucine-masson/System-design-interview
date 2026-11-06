"""English version of the system design best practices theme (same cards as the French one)."""

from api.course_models import CardTranslation, ThemeTranslation

SOURCE = "Principles of good system design (Sean Goedecke)"

THEME = ThemeTranslation(
    slug="system-design",
    titre="System design best practices",
    source_label=SOURCE,
    cards=[
        CardTranslation(
            titre="A good design is unobtrusive",
            accroche=(
                "A good system is recognized by how little it gets talked about: few "
                "incidents, few surprises."
            ),
            points=[
                "An impressive but complex design often hides a bad decision made early, "
                "whose consequences are paid for later.",
                "Start from a simple system that works, then add complexity only when a "
                "measured need requires it.",
                "Interview message: begin with the simplest architecture, then justify "
                "each added component by a precise problem.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Minimize state",
            accroche=(
                "State is what makes systems hard: you can restart a stateless service, "
                "not a corrupted database."
            ),
            points=[
                "A stateful component can get corrupted and is not fixed by a simple "
                "restart; it needs backups and care.",
                "Rule: a single service owns the database; the others go through its API "
                "or consume its events.",
                "Stateless services replicate easily behind a load balancer.",
                "Every new source of truth (cache, copy, external index) is one more state "
                "to keep consistent.",
            ],
            source_label=SOURCE,
            diagram_labels=["Service A", "Service B", "Owner service", "Database"],
            edge_labels=["API", "API"],
        ),
        CardTranslation(
            titre="Schemas and indexes",
            accroche=("A readable schema and well-suited indexes avoid most performance problems."),
            points=[
                "Design the schema with care: flexible but clear, with no catch-all "
                "key-value table or JSON column for everything.",
                "An index follows the real queries; for a composite index, put the most "
                "selective column first.",
                "Indexes speed up reads but slow down writes and take space: choose them, "
                "do not pile them up.",
                "Before adding a cache, check whether a missing index explains the slowness.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Let the database do the work",
            accroche=("A database joins and filters far better than application code."),
            points=[
                "Prefer a join to multiple round trips; avoid the N+1 problem (one query "
                "per item of a list).",
                "Send reads to replicas to relieve the primary database.",
                "Rate-limit bulk writes and large transactions, which can saturate the "
                "primary database.",
                "Measure with EXPLAIN before optimizing: fix what you have seen.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Take slow work out of the request",
            accroche=(
                "A user request quickly returns the useful minimum; the rest goes to a "
                "background task."
            ),
            points=[
                "Examples: sending an email, generating a report, calling a slow "
                "third-party API, a long LLM call.",
                "Default mechanism: a task queue with workers, which also handles retries.",
                "For tasks scheduled far in the future, a database table with a periodic "
                "check is simpler.",
                "Plan a visible task state (running, succeeded, failed) for the user.",
            ],
            source_label=SOURCE,
            diagram_labels=["Request", "Fast response", "Task queue", "Worker"],
        ),
        CardTranslation(
            titre="Use caching sparingly",
            accroche=("A cache is extra state that can go stale: I use it as a last resort."),
            points=[
                "First reflex: find out why it is slow (index, query, needless call) "
                "before caching.",
                "A cache raises questions: when to invalidate, what happens on a cold "
                "start, how to avoid stale data.",
                "If you cache, define a clear lifetime and explicitly accept the possible "
                "staleness.",
                "Object storage can serve as a large persistent cache for heavy, rarely "
                "modified data.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Events, direct calls, push and pull",
            accroche=(
                "Events are powerful but harder to follow: I choose them for specific needs."
            ),
            points=[
                "Events: suited to notifications with no reply expected and to large, "
                "non-urgent volumes.",
                "Direct calls: easier to trace and reason about, hence preferable in most cases.",
                "Pull (the consumer asks) is simpler; push suits rarely modified data "
                "that must reach many people.",
                "At very large scale, push goes through queues and workers that fan out to "
                "recipients.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Take care of critical paths",
            accroche=("I focus effort on the busiest and most important journeys."),
            points=[
                "Identify the flows that earn money or touch the most users: they deserve "
                "the most care.",
                "On these paths, few designs are good, and a mistake costs far more than "
                "elsewhere.",
                "For the rest, a simple, imperfect solution is enough.",
                "In an interview, announce upfront what the critical path is and size it first.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Log and measure",
            accroche=(
                "You do not fix what you cannot see: logs and metrics decide how fast you "
                "can diagnose."
            ),
            points=[
                "Log the decisions made, especially on failure or unusual paths, not only errors.",
                "Track resources and queues: CPU saturation, memory, queue lag.",
                "Look at p95 and p99 latencies rather than the average, which hides the "
                "worst experiences.",
                "Do not log sensitive data.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Plan for failures",
            accroche=(
                "Every component will eventually fail: I decide in advance how the system reacts."
            ),
            points=[
                "Killswitches to disable a problematic feature without redeploying.",
                "Careful retries: growing delay, circuit breaker and idempotency keys so "
                "the action is not duplicated.",
                "Choose per feature whether to fail open (for example a rate limiter that "
                "lets traffic through) or closed (an authentication that refuses).",
                "Test these behaviors: a simulated outage beats a surprise in production.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Prefer proven components",
            accroche=(
                "A good design applies well-known tools in the right places; it does not invent."
            ),
            points=[
                "A relational database, a task queue and a standard cache cover the vast "
                "majority of needs.",
                "Home-made code for what a proven tool already does adds maintenance and bugs.",
                "You gain in hiring, documentation and reliability by staying on common "
                "technologies.",
                'Justify any deviation: "why not the standard solution?" must have a '
                "measured answer.",
            ],
            source_label=SOURCE,
        ),
    ],
)
