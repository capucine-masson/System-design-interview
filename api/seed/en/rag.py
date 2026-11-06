"""English version of the RAG and search theme (same cards, same order as the French one)."""

from api.course_models import CardTranslation, ThemeTranslation

RAG_PAPER = 'Lewis et al., 2020, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"'
SBERT = 'Reimers and Gurevych, 2019, "Sentence-BERT"'
DPR = 'Karpukhin et al., 2020, "Dense Passage Retrieval"'
HNSW = 'Malkov and Yashunin, "Hierarchical Navigable Small World graphs"'
CHUNKING = 'Pinecone, "Chunking Strategies for LLM Applications"'
RERANK = 'Nogueira and Cho, 2019, "Passage Re-ranking with BERT"'
EVALS = "AI Evals FAQ (Hamel Husain)"

THEME = ThemeTranslation(
    slug="rag",
    titre="RAG and search",
    source_label="Public articles and guides, cited card by card",
    cards=[
        CardTranslation(
            titre="Why RAG",
            accroche=(
                "RAG gives the model the right documents at answer time, instead of "
                "relying on its memory."
            ),
            points=[
                "Problems targeted: outdated knowledge, private data the model has never "
                "seen, hallucinations on precise facts.",
                "Principle: retrieve relevant passages, insert them in the prompt, "
                "generate an answer grounded in them, with possible citations.",
                "Updating the document base is enough, with no retraining of the model.",
                "RAG or fine-tuning? RAG brings facts, fine-tuning brings a style or a "
                "behavior; they are sometimes combined.",
            ],
            source_label=RAG_PAPER,
            diagram_labels=["Question", "Search", "Passages", "LLM", "Cited answer"],
        ),
        CardTranslation(
            titre="Embeddings",
            accroche=(
                "An embedding turns a text into a vector, so that texts with close "
                "meanings give close vectors."
            ),
            points=[
                "A bi-encoder encodes the question and each document separately; they are "
                "then compared by cosine similarity or dot product.",
                "Documents are encoded once in advance; only the question is encoded at "
                "query time, hence the speed.",
                "Typical dimensions: from a few hundred to about 3,000; larger means more "
                "memory and search time.",
                "Choose by language (multilingual for French), domain, maximum input "
                "length and cost; then measure on your own data.",
            ],
            source_label=SBERT,
        ),
        CardTranslation(
            titre="Chunking",
            accroche=(
                "Splitting documents into well-sized pieces is often the setting that "
                "influences RAG quality the most."
            ),
            points=[
                "Too big: the passage dilutes the information and eats context; too "
                "small: the context needed to understand is lost.",
                "Starting order of magnitude: a few hundred tokens, with a 10 to 20% "
                "overlap between chunks.",
                "Better to split along structure (headings, paragraphs, code functions) "
                "than by blind fixed size.",
                "Store metadata (title, section, date, source) to filter and to cite.",
                "Test several sizes and keep the one that maximizes recall on your own questions.",
            ],
            source_label=CHUNKING,
        ),
        CardTranslation(
            titre="Vector databases and approximate search",
            accroche=(
                "A vector database quickly finds the closest vectors among millions, "
                "accepting an approximation."
            ),
            points=[
                "Exact search compares against every vector: linear cost, too slow at large scale.",
                "HNSW builds a layered graph: you descend layer by layer following the "
                "nearest neighbors; a very good recall/latency trade-off.",
                "Other families: inverted index by clusters (IVF) and vector compression "
                "(product quantization) to save memory.",
                "Settings to quote: target recall, latency, memory, and metadata "
                "filtering combined with search.",
                "For a few thousand documents, a plain exact search or a database "
                "extension is enough.",
            ],
            source_label=HNSW,
        ),
        CardTranslation(
            titre="Dense retrieval",
            accroche=(
                "Dense retrieval compares meanings rather than words: it finds passages "
                "even with no word in common."
            ),
            points=[
                "A learned encoder, trained on question-passage pairs, places the right "
                "pairs close together in vector space.",
                "Strength: synonyms, paraphrases, natural-language questions.",
                "Weakness: rare terms, identifiers, proper nouns, error codes, which "
                "lexical search finds better.",
                "It depends on the training domain: test it on your own documents before "
                "relying on it.",
            ],
            source_label=DPR,
        ),
        CardTranslation(
            titre="Hybrid search",
            accroche=(
                "Lexical search (BM25) and dense search are combined to cover both exact "
                "words and meaning."
            ),
            points=[
                "BM25 scores documents by the frequency of the question's words, weighted "
                "by their rarity and the document length.",
                "Both searches run in parallel, then the lists are merged, often by rank "
                "fusion (RRF), which avoids comparing scores of different natures.",
                "This combination is a good default for documents mixing prose and "
                "technical terms.",
                "Cost: two indexes to maintain and one more fusion step.",
            ],
            source_label='Robertson and Zaragoza, 2009, "The Probabilistic Relevance Framework"',
            diagram_labels=["Question", "BM25", "Vectors", "Fusion (RRF)"],
        ),
        CardTranslation(
            titre="Reranking",
            accroche=(
                "A fast search retrieves broadly, then a more precise model reorders the "
                "best candidates."
            ),
            points=[
                "A cross-encoder reads the question and the passage together: more "
                "precise than a bi-encoder, but too slow for the whole base.",
                "Common pattern: retrieve 50 to 100 candidates, rerank, keep the best 5 "
                "to 10 for the prompt.",
                "Typical gain in the relevance of the first results, at the price of a "
                "few tens to hundreds of ms of extra latency.",
                "Add it when the right passages are among the candidates but badly "
                "ranked: you see it with recall@k versus precision@k.",
            ],
            source_label=RERANK,
            diagram_labels=["Question", "Fast top 100", "Reranker", "Top 5 to the LLM"],
        ),
        CardTranslation(
            titre="Building the generation prompt",
            accroche=(
                "The prompt must tell the model to rely on the provided passages and to "
                "admit when they are not enough."
            ),
            points=[
                "Delimit the passages clearly (tags, numbers) and present them as data, "
                "not as instructions.",
                "Ask it to answer only from the context, to cite the passages used, and "
                'to say "I don\'t know" otherwise.',
                "Mind where information sits: models sometimes use passages in the middle "
                "of a long context poorly.",
                "Limit the number of passages: more is not always better, noise degrades "
                "the answer and costs tokens.",
                "A retrieved document may contain malicious instructions (prompt "
                "injection): never execute them.",
            ],
            source_label=RAG_PAPER,
        ),
        CardTranslation(
            titre="Evaluating retrieval",
            accroche=(
                "Retrieval is evaluated on its own first: did we find the right passages, "
                "and well ranked?"
            ),
            points=[
                "Build a set of questions with the passages that answer them, by hand or "
                "by generating questions from the documents.",
                "Recall@k: is the right answer in the top k? It is the key metric, since "
                "the LLM cannot use what it does not receive.",
                "MRR and nDCG add the position of the right passage in the ranking.",
                "For retrieval, these ranking metrics are suitable, unlike generic scores "
                "on generated text.",
            ],
            source_label=EVALS,
        ),
        CardTranslation(
            titre="Evaluating generation and diagnosing",
            accroche=(
                "Once retrieval is measured, check that the answer is faithful to the "
                "passages and answers the question."
            ),
            points=[
                "Faithfulness (groundedness): is each claim supported by the provided "
                "passages? An LLM judge validated on human labels can handle it.",
                "Answer relevance: does it really answer the question asked, without digressing?",
                "Diagnosis: wrong passage retrieved, right passage ignored, or bad "
                "generation? Each cause has its fix (retrieval, prompt, model).",
                "Start from error analysis on real traces before choosing metrics.",
            ],
            source_label=EVALS,
        ),
        CardTranslation(
            titre="Improving a disappointing RAG",
            accroche=(
                "When RAG answers badly, I first look for where it fails, then apply the "
                "matching lever."
            ),
            points=[
                "Query rewriting: rephrase a vague question or enrich it with the "
                "conversation history before searching.",
                "Retrieve small precise chunks but give the model the parent paragraph or "
                "section to keep the context.",
                "Metadata filters (date, product, access rights) to narrow the search scope.",
                "Add hybrid search then reranking if recall is insufficient.",
                "Access rights must apply to retrieval: a user must not read through RAG "
                "what they cannot open.",
            ],
            source_label="Synthesis of common practices",
        ),
    ],
)
