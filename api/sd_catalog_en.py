"""Version anglaise du catalogue des cas (même slugs que `sd_catalog.py`)."""

from pydantic import BaseModel


class CaseText(BaseModel):
    """Titre, description et axes d'un type de cas dans une langue."""

    titre: str
    description: str
    axes: list[str]


CASE_TEXTS_EN: dict[str, CaseText] = {
    "rag": CaseText(
        titre="RAG over a large document base",
        description="Answer questions about a very large corpus of internal documents.",
        axes=[
            "document volume and update rate",
            "chunking and embeddings",
            "vector database and reranking",
            "retrieval evaluation",
            "hallucinations and citations",
            "access rights",
        ],
    ),
    "inference": CaseText(
        titre="Large-scale LLM inference service",
        description="Serve an LLM to many users under latency and cost constraints.",
        axes=[
            "traffic and load spikes",
            "time to first token versus throughput",
            "GPUs, continuous batching, KV cache",
            "quantization",
            "autoscaling and streaming",
            "cost per token",
        ],
    ),
    "entrainement": CaseText(
        titre="Training or fine-tuning pipeline",
        description="Train or adapt a model on proprietary data.",
        axes=[
            "data collection, cleaning and deduplication",
            "model size and compute budget",
            "data, tensor and pipeline parallelism",
            "checkpointing and failure recovery",
            "LoRA versus full fine-tuning",
            "evaluation before deployment",
        ],
    ),
    "evaluation": CaseText(
        titre="LLM evaluation platform",
        description="Reliably and continuously measure the quality of models and prompts.",
        axes=[
            "benchmarks and internal test sets",
            "LLM-as-judge and how to validate it",
            "human evaluation",
            "regression detection",
            "A/B tests in production",
            "evaluation cost and frequency",
        ],
    ),
    "agent": CaseText(
        titre="Agent or assistant with tools",
        description="An assistant that plans and calls tools to complete tasks.",
        axes=[
            "tools and permissions",
            "memory and context",
            "guardrails and irreversible actions",
            "reliability over several steps",
            "observability and evaluation",
            "latency and cost per task",
        ],
    ),
    "recommandation": CaseText(
        titre="ML-based recommendation or moderation",
        description="An ML system that ranks or filters content continuously.",
        axes=[
            "event volume and decision latency",
            "feature store and online/offline data",
            "model training and deployment",
            "monitoring and data drift",
            "false positives, fairness and human in the loop",
            "cold start",
        ],
    ),
    "google-docs": CaseText(
        titre="Collaborative document editor (like Google Docs)",
        description="Several people edit the same document in real time.",
        axes=[
            "concurrent editors and document size",
            "conflict resolution (OT or CRDT)",
            "real-time sync and offline mode",
            "version history and restore",
            "sharing rights and comments",
            "storage and disaster recovery",
        ],
    ),
    "streaming-video": CaseText(
        titre="Video on demand streaming (like Netflix, YouTube)",
        description="Deliver videos to millions of viewers worldwide.",
        axes=[
            "catalog, duration and volume of videos",
            "multi-resolution encoding and adaptive bitrate",
            "CDN and edge caches",
            "traffic spikes on release days",
            "resume playback and recommendations",
            "storage and bandwidth cost",
        ],
    ),
    "url-shortener": CaseText(
        titre="URL shortener",
        description="Turn long URLs into short links and redirect quickly.",
        axes=[
            "creations and redirects per second",
            "unique identifier generation",
            "link lifetime and expiration",
            "cache and redirect latency",
            "click statistics",
            "abuse and malicious links",
        ],
    ),
    "messagerie": CaseText(
        titre="Instant messaging (like WhatsApp)",
        description="Send messages between users, live and in groups.",
        axes=[
            "connected users and messages per second",
            "persistent connections (WebSocket)",
            "ordering, guaranteed delivery and read receipts",
            "groups and fan-out",
            "history storage",
            "presence and offline notifications",
        ],
    ),
    "fil-actualite": CaseText(
        titre="Social network news feed (like X, Instagram)",
        description="Show each user a feed of posts from the people they follow.",
        axes=[
            "users, posts and reads per second",
            "fan-out on write versus on read",
            "accounts with very many followers",
            "feed ranking",
            "media and caching",
            "consistency and freshness",
        ],
    ),
    "vtc": CaseText(
        titre="Ride-hailing service (like Uber)",
        description="Match riders with nearby drivers in real time.",
        axes=[
            "active drivers and location update rate",
            "geospatial index and proximity search",
            "matching and peak handling",
            "real-time ride tracking",
            "dynamic pricing",
            "fault tolerance and payment",
        ],
    ),
    "stockage-fichiers": CaseText(
        titre="File storage and sync (like Dropbox)",
        description="Store files and sync them across several devices.",
        axes=[
            "users, stored volume and file size",
            "chunking and deduplication",
            "sync and conflict handling",
            "sharing and permissions",
            "versions and trash",
            "durability and storage cost",
        ],
    ),
    "rate-limiter": CaseText(
        titre="Distributed rate limiter",
        description="Limit the number of requests per client on a distributed API.",
        axes=[
            "requests per second and number of clients",
            "algorithms (sliding window, token bucket)",
            "shared state and consistency across nodes",
            "latency added to each request",
            "per-client or per-route rules",
            "behavior on failure",
        ],
    ),
    "notifications": CaseText(
        titre="Notification system (push, email, SMS)",
        description="Reliably send notifications to millions of users.",
        axes=[
            "send volume and campaign spikes",
            "queues and priorities",
            "preferences and unsubscribes",
            "retries and idempotence",
            "external provider limits",
            "delivery tracking",
        ],
    ),
    "autocompletion": CaseText(
        titre="Search suggestions (autocomplete)",
        description="Suggest completions while the user types a query.",
        axes=[
            "requests per second and target latency",
            "data structure (prefix tree)",
            "ranking by popularity and freshness",
            "suggestion updates",
            "personalization",
            "content to filter out",
        ],
    ),
    "crawler": CaseText(
        titre="Web crawler",
        description="Browse and download web pages at scale.",
        axes=[
            "number of pages and refresh frequency",
            "URL queue and priorities",
            "politeness toward sites (robots.txt)",
            "duplicate detection",
            "fault tolerance and resumption",
            "page storage and processing",
        ],
    ),
    "paiement": CaseText(
        titre="Online payment system (like Stripe)",
        description="Process payments reliably, without double charges.",
        axes=[
            "transactions per second and spikes",
            "idempotence and double-charge prevention",
            "consistency and distributed transactions",
            "integration with banks and providers",
            "accounting reconciliation",
            "security and compliance",
        ],
    ),
    "billetterie": CaseText(
        titre="Ticket booking (like Ticketmaster)",
        description="Sell limited seats for highly demanded events.",
        axes=[
            "demand spike when sales open",
            "temporary holds and expiration",
            "avoiding overselling (concurrency)",
            "virtual waiting room",
            "payment and cancellation",
            "fairness against bots",
        ],
    ),
    "kv-store": CaseText(
        titre="Distributed key-value store",
        description="Design a distributed key-value store that is fast and fault tolerant.",
        axes=[
            "data volume and operations per second",
            "partitioning and rebalancing",
            "replication and consistency levels",
            "fault tolerance and recovery",
            "read and write latency",
            "compaction and on-disk storage",
        ],
    ),
    "sessions-utilisateur": CaseText(
        titre="User session management (login, logout, expiration)",
        description="Authenticate users and manage their sessions securely.",
        axes=[
            "active users and logins per second",
            "server-side sessions or tokens (JWT)",
            "session storage (shared cache)",
            "expiration, renewal and logout on all devices",
            "session theft and security",
            "fault tolerance and scaling",
        ],
    ),
    "permissions": CaseText(
        titre="Permission management (roles and access control)",
        description="Decide who can do what on which resources, across a whole organization.",
        axes=[
            "users, resources and checks per second",
            "access model (RBAC, ABAC, inheritance)",
            "check latency and caching",
            "revocation and propagation of changes",
            "audit log",
            "administration and delegation of rights",
        ],
    ),
    "commandes-en-ligne": CaseText(
        titre="Online orders with a shopping cart (e-commerce)",
        description="Handle the cart, order creation, tracking and cancellation.",
        axes=[
            "orders per second and spikes (sales)",
            "cart and stock reservation",
            "order states and tracking",
            "cancellation, refunds and consistency",
            "payment and idempotence",
            "notifications and logistics integration",
        ],
    ),
    "bibliotheque": CaseText(
        titre="Library book management",
        description="Add, remove and search books, and manage loans.",
        axes=[
            "number of books, copies and users",
            "data model (book, copy, loan)",
            "search by title, author or subject",
            "loans, returns and reservations",
            "concurrency on the same copy",
            "multiple sites and catalog evolution",
        ],
    ),
    "blog": CaseText(
        titre="Blog platform",
        description="Create, edit, delete and publish posts read by many people.",
        axes=[
            "authors, posts and reads per second",
            "data model and drafts",
            "caching and delivery of published pages",
            "search, tags and comments",
            "editor, media and versions",
            "moderation and content safety",
        ],
    ),
    "moe-serving": CaseText(
        titre="Serving a 70B Mixture-of-Experts model with a p95 latency target",
        description="Serve a large MoE to many users while holding a p95 latency.",
        axes=[
            "traffic, prompt lengths and p95 latency target",
            "expert routing and load balancing",
            "expert, tensor and pipeline parallelism across GPUs",
            "GPU memory budget (weights, KV cache, activations)",
            "continuous batching and the latency versus throughput trade-off",
            "quantization, GPU failures and cost per token",
        ],
    ),
    "api-multi-tenant": CaseText(
        titre="Rate limiting and capacity allocation for a multi-tenant LLM API",
        description="Share GPU capacity fairly between customers with different SLAs.",
        axes=[
            "customers, SLA tiers and available GPU capacity",
            "token and request quotas per minute",
            "fairness between customers (noisy neighbor) and priority queues",
            "bursts, rejecting versus queueing, graceful degradation",
            "shared counter state across regions and added latency",
            "metering, billing and per-customer alerts",
        ],
    ),
    "lora-multi-adaptateurs": CaseText(
        titre="Fine-tuning and multi-adapter LoRA serving for customers",
        description="Offer each customer an adapted model without a dedicated GPU per customer.",
        axes=[
            "number of customers and dataset sizes",
            "LoRA fine-tuning pipeline and evaluation before release",
            "a shared base model and adapters loaded on demand",
            "GPU memory, adapter cache and cold start",
            "data and performance isolation between customers",
            "versions, rollback and cost per customer",
        ],
    ),
}
