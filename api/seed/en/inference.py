"""English version of the inference optimization theme (same cards, same order as the French)."""

from api.course_models import CardTranslation, ThemeTranslation

SOURCE = "Large Transformer Model Inference Optimization (Lilian Weng, 2023)"
FAIRNESS = 'Sheng et al., 2024, "Fairness in Serving Large Language Models"'
MIXTRAL = 'Jiang et al., 2024, "Mixtral of Experts"'

THEME = ThemeTranslation(
    slug="inference",
    titre="Inference optimization",
    source_label=SOURCE,
    cards=[
        CardTranslation(
            titre="Prefill and decode: two regimes",
            accroche=(
                "Serving an LLM means two very different phases: reading the prompt in one "
                "go, then generating the answer token by token."
            ),
            points=[
                "Prefill processes the whole prompt in parallel: lots of compute, the GPU "
                "is limited by its compute power (compute-bound).",
                "Decode produces one token at a time: every step rereads all the weights "
                "and the KV cache, so it is limited by memory bandwidth.",
                "Three metrics to quote: TTFT (time to first token), time per generated "
                "token, and overall throughput in tokens per second.",
                "Almost every optimization targets one of the two regimes: reduce the bytes "
                "read at decode, or fill the GPU better.",
            ],
            source_label=SOURCE,
            diagram_labels=["Prompt", "Prefill (parallel)", "Decode (token by token)", "Answer"],
        ),
        CardTranslation(
            titre="KV cache",
            accroche=(
                "The KV cache keeps the keys and values already computed so attention is "
                "not redone over the whole past for every new token."
            ),
            points=[
                "Without a cache, every generated token would recompute K and V for the "
                "whole context; with one, only the new token is computed and the rest is read.",
                "Approximate size: 2 (K and V) × layers × KV heads × head dimension × "
                "bytes × tokens × batch size.",
                "Example to quote: a classic 7B model in fp16 (32 layers, dimension 4096) "
                "costs about 0.5 MB per token, i.e. ~2 GB for 4,000 tokens per request.",
                "Consequence: the cache, not the weights, often limits the number of "
                "simultaneous requests on a GPU.",
            ],
            source_label=SOURCE,
            diagram_labels=[
                "New token",
                "Compute its Q, K, V",
                "Append K, V to cache",
                "Attention",
            ],
        ),
        CardTranslation(
            titre="Reducing the KV cache cost",
            accroche=(
                "Several levers let you fit more context and more requests: fewer KV "
                "heads, fewer tokens kept, memory pages."
            ),
            points=[
                "Multi-query and grouped-query attention share keys and values across "
                "several heads: the cache is divided by the number of groups.",
                "Sliding-window attention keeps only the latest tokens, at the price of a "
                "limited view of the beginning.",
                "PagedAttention (vLLM) splits the cache into pages like virtual memory: no "
                "more fragmentation, so more requests in parallel.",
                "The cache can also be quantized to 8 bits, or a common prefix (system "
                "prompt) can be reused across requests.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Quantization",
            accroche=(
                "Quantizing means storing weights, and sometimes activations, with fewer "
                "bits to cut memory and speed up reads."
            ),
            points=[
                "Order of magnitude: a 7B model weighs ~14 GB in fp16, ~7 GB in int8 and "
                "~3.5 GB in int4, not counting the cache.",
                "Post-training quantization (PTQ) is done on an already trained model with "
                "little data; QAT retrains, which costs more but is more accurate.",
                "The trap: a few outlier activations break naive quantization; LLM.int8() "
                "and SmoothQuant handle them.",
                "Common weight methods: GPTQ and AWQ. At 8 bits the loss is often "
                "negligible; at 4 bits you must measure on your own task.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Continuous batching",
            accroche=(
                "Continuous batching inserts new requests into the batch as soon as "
                "another one finishes, instead of waiting for the whole batch to end."
            ),
            points=[
                "Static batching waits for the longest request: the others leave an empty "
                "slot and the GPU is underused.",
                "Continuous batching schedules at every decode iteration: a finished "
                "request frees its slot right away.",
                "Result: several times more throughput for comparable latency; it is the "
                "default behavior of vLLM or TGI.",
                "Trade-off: a bigger batch raises throughput but lengthens each request's "
                "latency, hence tuning against the SLO.",
            ],
            source_label=SOURCE,
            diagram_labels=["Request queue", "Scheduler (every iteration)", "GPU: running batch"],
            edge_labels=["adds", "frees"],
        ),
        CardTranslation(
            titre="Multi-GPU parallelism",
            accroche=(
                "When the model does not fit on one GPU, it is split: by layers, by "
                "matrices or by experts."
            ),
            points=[
                "Order of magnitude: 70B in fp16 is ~140 GB of weights, more than the 80 GB "
                "of a high-end GPU.",
                "Tensor parallelism: each matrix is split across GPUs, with communication "
                "at every layer; keep it inside a node (fast links).",
                "Pipeline parallelism: each GPU carries a group of layers; efficient "
                "across nodes but creates idle bubbles.",
                "Data parallelism: the model is duplicated to serve more requests; MoEs "
                "add expert parallelism.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Distillation",
            accroche=(
                "A small model is trained to imitate a big one: most of the quality is "
                "kept for a fraction of the cost."
            ),
            points=[
                "The student learns to reproduce the teacher's probabilities (soft "
                "labels), which are richer than a single right answer.",
                "Classic example: DistilBERT, about 40% smaller and 60% faster than BERT "
                "for ~97% of its performance.",
                "For LLMs, distillation also goes through data: a big model generates "
                "answers or reasoning traces on which the small one is fine-tuned.",
                "Limit: the student does not outdo its teacher, and you have to pay for "
                "data generation and training.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Pruning and sparsity",
            accroche=(
                "Pruning means removing weights or structures of little use to make the "
                "model lighter."
            ),
            points=[
                "Unstructured pruning zeroes individual weights: good compression ratio, "
                "but little real gain without hardware support.",
                "Structured pruning removes heads, neurons or whole layers: real speedup, "
                "sharper quality loss.",
                "Recent GPUs accelerate 2:4 sparsity (2 zeros out of 4 weights) for about "
                "2× on matrix multiplications.",
                "Methods like SparseGPT prune an LLM in one pass, without retraining, up "
                "to ~50% of weights with little loss.",
            ],
            source_label=SOURCE,
        ),
        CardTranslation(
            titre="Speculative decoding",
            accroche=(
                "A small model guesses a few tokens, the big model checks them all in a "
                "single pass: generation is faster without changing the output."
            ),
            points=[
                "The draft model proposes k tokens (for example 4 to 8) at low cost.",
                "The big model computes in parallel the probabilities of these k positions "
                "and accepts the longest consistent prefix.",
                "Accept/reject sampling guarantees exactly the same distribution as the "
                "big model alone: no quality loss.",
                "Typical gain of 2 to 3×, depending on the acceptance rate: effective on "
                "predictable text, less on creative text.",
            ],
            source_label=SOURCE,
            diagram_labels=["Draft: k tokens", "Big model verifies", "Keep the valid prefix"],
        ),
        CardTranslation(
            titre="Mixture of Experts (MoE)",
            accroche=(
                "An MoE replaces the feed-forward with several experts and activates only "
                "a few per token: many parameters, little compute."
            ),
            points=[
                "A router picks the k best experts for each token; Mixtral 8x7B activates "
                "2 out of 8.",
                "Figures to quote: Mixtral has ~47 billion parameters in total but uses "
                "only about 13 billion per token.",
                "Compute per token follows the active parameters, but memory must hold all "
                "the experts: several GPUs are needed.",
                "Difficulties: balancing load across experts, keeping an expert from "
                "being saturated, and handling communication between GPUs.",
            ],
            source_label=SOURCE,
            diagram_labels=["Token", "Router", "Expert 1", "Expert 2", "Expert N", "Weighted sum"],
            edge_labels=["top-k", "top-k"],
        ),
        CardTranslation(
            titre="Fair scheduling and token quotas",
            accroche=(
                "On a shared LLM API, limiting and scheduling are done in tokens, not "
                "requests, to share GPU capacity fairly between customers with different "
                "SLAs."
            ),
            points=[
                "A 100,000-token request weighs far more than a thousand small ones: limit "
                "in tokens per minute (input and output), on top of requests per minute.",
                "At admission, reserve the maximum requested output (max_tokens), then "
                "give the unused part back to the customer's token bucket.",
                "SLA tiers: weights and priority queues per tier, reserved capacity for "
                "premium customers, the rest best-effort, bursts allowed up to a ceiling.",
                "Fairness: keep a big customer from monopolizing the GPUs (noisy "
                "neighbor) by serving first whoever received the fewest tokens (Virtual "
                "Token Counter), on top of continuous batching.",
                "Under overload: reject fast with a 429 and a retry delay rather than let "
                "the queue grow, or degrade (smaller model).",
                "To track: p95 per tier, rejection rate, queue wait time, GPU utilization.",
            ],
            source_label=FAIRNESS,
            diagram_labels=[
                "Customer request",
                "Token quota",
                "Queue per tier",
                "Fair scheduler",
                "GPU",
            ],
        ),
        CardTranslation(
            titre="Expert routing and load balancing",
            accroche=(
                "In an MoE served across several GPUs, the router sends each token to a "
                "few experts: the difficulty is keeping the GPUs balanced and "
                "communication cheap."
            ),
            points=[
                "In Mixtral, each layer has 8 experts and the router picks 2 per token, a "
                "choice that can change at every token and every layer.",
                "Expert parallelism: experts are spread across GPUs, and each layer needs "
                "an all-to-all exchange to send tokens to their experts and bring them back.",
                "Imbalance: if one expert is heavily used, its GPU becomes the straggler "
                "and sets the step time for everyone (hence the p95).",
                "At training, an auxiliary balancing loss spreads the tokens; at "
                "inference, monitor per-expert load and replicate hot experts if needed.",
                "Memory: all experts must fit in GPU memory even if few are active; with "
                "large batches, almost all of them are read at every step.",
                "Budget to work out: weights (~47 billion parameters for Mixtral) + KV "
                "cache + activations, against the memory available per GPU.",
            ],
            source_label=MIXTRAL,
            diagram_labels=[
                "Token",
                "Router (top-k)",
                "Experts on GPU 1",
                "Experts on GPU 2",
                "Weighted sum",
            ],
            edge_labels=["all-to-all", "all-to-all"],
        ),
    ],
)
