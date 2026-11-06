"""English version of the Transformers theme (same cards, same order as the French one)."""

from api.course_models import CardTranslation, ThemeTranslation

SOURCE = "The Illustrated Transformer (Jay Alammar)"
PAPER = 'Vaswani et al., 2017, "Attention Is All You Need"'

THEME = ThemeTranslation(
    slug="transformers",
    titre="Transformers",
    source_label=SOURCE,
    cards=[
        CardTranslation(
            titre="Why the Transformer?",
            accroche=(
                "The Transformer replaces recurrence with attention, so all the words of a "
                "sentence can be processed in parallel."
            ),
            points=[
                "Before 2017 we used RNNs and LSTMs: they read the text word by word, so "
                "training cannot be parallelized across a sequence.",
                "Another RNN limit: information from the start of the sentence fades with "
                "distance, so long-range dependencies are poorly learned.",
                'The paper "Attention Is All You Need" (Google, 2017) proposes an '
                "architecture with no recurrence, based only on attention.",
                "Result: training that parallelizes very well on GPUs, so models could be "
                "scaled to billions of parameters.",
            ],
            source_label=PAPER,
            diagram_labels=["Text", "Embeddings + positions", "Attention blocks", "Prediction"],
        ),
        CardTranslation(
            titre="Tokenization",
            accroche=(
                "The model does not read words but tokens: pieces of words chosen to cover "
                "any language with a fixed-size vocabulary."
            ),
            points=[
                "Most often BPE is used: start from characters and merge the most frequent "
                "pairs until the target vocabulary size is reached.",
                "Vocabularies typically hold between 32,000 and more than 128,000 tokens; "
                "a rare word is split into several sub-words, a common word stays whole.",
                "Order of magnitude to quote: about 3 to 4 characters per token in English; "
                "French and code use a few more tokens for the same text.",
                "It matters for cost and latency: you pay for, and fill the context window "
                "with, tokens, not words.",
                "Strange errors on digits, spelling or anagrams often come from here: the "
                "model does not see letters.",
            ],
            source_label=SOURCE,
            diagram_labels=["Raw text", "BPE split", "IDs", "Embeddings"],
        ),
        CardTranslation(
            titre="Embeddings and positional encoding",
            accroche=(
                "Each token becomes a vector, to which position information is added, "
                "because attention alone does not know word order."
            ),
            points=[
                "An embedding is a learned vector per token; in the original paper its "
                "dimension is 512 (called d_model).",
                "Attention treats tokens as a set: shuffle the order and the result is the "
                "same. Position therefore has to be injected.",
                "Original version: sinusoids of different frequencies added to the "
                "embeddings. They generalize a little to unseen lengths.",
                "Today most LLMs use RoPE (rotary embeddings): query and key vectors are "
                "rotated according to their position, which encodes a relative distance.",
            ],
            source_label=SOURCE,
            diagram_labels=["Token", "Embedding", "+ position", "Block input"],
        ),
        CardTranslation(
            titre="Self-attention",
            accroche=(
                "For each token, self-attention computes a weighted average of all the "
                "other tokens, with weights that depend on content."
            ),
            points=[
                "Each token produces three vectors through learned projections: a query Q "
                "(what I look for), a key K (what I offer), a value V (what I bring).",
                "Q and K are compared with a dot product, divided by the square root of "
                "d_k, then softmax: this gives weights that sum to 1.",
                "The output is the sum of the values V weighted by these weights. Formula "
                "to say out loud: softmax(Q·Kᵀ / √d_k) · V.",
                "Dividing by √d_k keeps dot products from growing large and saturating the "
                "softmax, which would kill the gradients.",
                'Spoken example: in "the bank closed because it was empty", "it" should '
                'weight "bank" heavily.',
            ],
            source_label=SOURCE,
            diagram_labels=["Input X", "Q", "K", "V", "Softmax(QKᵀ/√d)", "Output"],
            edge_labels=["weights"],
        ),
        CardTranslation(
            titre="Multi-head attention",
            accroche=(
                "Instead of a single attention, several run in parallel on smaller "
                "subspaces, to capture several kinds of relations."
            ),
            points=[
                "In the paper: 8 heads, with d_model = 512, so each head works in dimension "
                "64. The total cost stays close to one big attention.",
                "Each head has its own Q, K, V projections: one can follow syntax, another "
                "coreferences, another proximity.",
                "The outputs of all heads are concatenated, then an output projection W_O "
                "brings them back to the model dimension.",
                "Variants to know for inference: multi-query and grouped-query attention "
                "share keys and values across heads to shrink the KV cache.",
            ],
            source_label=SOURCE,
            diagram_labels=["Input", "Head 1", "Head 2", "Head N", "Concat + W_O"],
        ),
        CardTranslation(
            titre="Feed-forward, residuals and normalization",
            accroche=(
                "Around attention, each block adds a small dense network applied token by "
                "token, residual connections and a normalization."
            ),
            points=[
                "The feed-forward is a two-layer MLP applied independently at each "
                "position; in the paper: 512 up to 2048 then back to 512.",
                "This is where most of a block's parameters live: about two thirds, "
                "against one third for attention.",
                "The residual connection adds the input to the output of each sub-layer: "
                "it helps gradients propagate through very deep networks.",
                "LayerNorm stabilizes training. Recent LLMs normalize before the sub-layer "
                "(pre-norm), often with RMSNorm, which is simpler and faster.",
            ],
            source_label=SOURCE,
            diagram_labels=["Input", "Attention", "Add & Norm", "Feed-forward", "Add & Norm"],
        ),
        CardTranslation(
            titre="Causal mask and autoregressive generation",
            accroche=(
                "A language model generates one token at a time, and the causal mask stops "
                "it from looking at future tokens during training."
            ),
            points=[
                "The mask sets scores toward future positions to minus infinity before the "
                "softmax: the attention matrix becomes triangular.",
                "Thanks to it, we train on the whole sequence at once (teacher forcing) "
                "while still simulating token-by-token generation.",
                "At inference we loop: predict the distribution of the next token, sample, "
                "append the token to the input, repeat.",
                "Sampling is tuned with temperature and top-p: low temperature for stable "
                "outputs, higher for diversity.",
                "This sequential loop is the reason for the KV cache: it avoids recomputing "
                "the keys and values of tokens already seen.",
            ],
            source_label=SOURCE,
            diagram_labels=["Prompt + generated tokens", "Model", "Distribution", "New token"],
            edge_labels=["sampling", "loop"],
        ),
        CardTranslation(
            titre="Encoder, decoder and cross-attention",
            accroche=(
                "The original Transformer has two stacks: an encoder that understands the "
                "input and a decoder that generates the output relying on it."
            ),
            points=[
                "The encoder stacks bidirectional self-attention blocks: each token sees "
                "the whole sentence. In the paper: 6 blocks.",
                "The decoder also stacks 6 blocks, with a masked self-attention followed "
                "by a cross-attention to the encoder output.",
                "In cross-attention, queries come from the decoder, keys and values from "
                'the encoder: this is how translation "looks at" the source.',
                "Three families to quote: encoder-only (BERT, to classify or embed), "
                "decoder-only (GPT, Mistral, Llama), encoder-decoder (T5).",
                "Today general-purpose LLMs are almost all decoder-only: simpler to scale "
                "and to train on raw text.",
            ],
            source_label=PAPER,
            diagram_labels=["Input", "Encoder (6 blocks)", "Decoder (6 blocks)", "Output"],
            edge_labels=["cross-attn"],
        ),
        CardTranslation(
            titre="Complexity and context window",
            accroche=(
                "Attention compares each token with all the others: its cost grows with the "
                "square of the length, which limits the context window."
            ),
            points=[
                "For n tokens, the attention matrix is n by n: time and memory in O(n²). "
                "Doubling the context multiplies this term by four.",
                "Feed-forwards, by contrast, are linear in n; on long contexts attention "
                "dominates.",
                "FlashAttention does not change the result but computes by blocks in fast "
                "GPU memory, which avoids materializing the full matrix.",
                "Other levers: sliding-window attention (used in Mistral 7B) and "
                "grouped-query attention to lighten the KV cache.",
                "Interview message: a long context is not free, it costs latency, GPU "
                'memory and often quality (information "lost in the middle").',
            ],
            source_label=PAPER,
            diagram_labels=["Context n", "n × n matrix", "Memory and compute in n²"],
        ),
        CardTranslation(
            titre="Training: predicting the next token",
            accroche=(
                "A decoder-type LLM is trained with a very simple objective: predict the "
                "next token, on enormous amounts of text."
            ),
            points=[
                "The loss is a cross-entropy between the predicted distribution and the "
                "true next token, computed at every position of the sequence.",
                "This pre-training gives a model that completes text, not yet an assistant: "
                "instruction fine-tuning comes next.",
                "Then an alignment with human preferences (RLHF, DPO) so that the model "
                "follows instructions and refuses what it should.",
                "Scaling laws link performance, model size, amount of data and compute: "
                "for a given budget there is a balance to aim for.",
            ],
            source_label=SOURCE,
            diagram_labels=["Pre-training", "Instruction fine-tuning", "Alignment", "Chat model"],
        ),
    ],
)
