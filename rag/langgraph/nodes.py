from rag.cache.memory_cache import (
    MemoryCache
)

from rag.query.query_understanding import (
    QueryUnderstanding
)

from rag.retrieval.hybrid import (
    HybridRetriever
)

from rag.retrieval.rerank import (
    Reranker
)

from rag.generation.prompt import (
    build_prompt
)

from rag.generation.llm import (
    GroqLLM
)

from rag.compression.compressor import (
    ContextCompressor
)

from rag.refinement.context_refiner import (
    ContextRefiner
)

# ==============================================
# INITIALIZE COMPONENTS
# ==============================================

cache = MemoryCache()

query_understanding = QueryUnderstanding()

retriever = HybridRetriever()

reranker = Reranker()

llm = GroqLLM()

compressor = ContextCompressor()

refiner = ContextRefiner(

    max_sentences_per_document=5,

    min_keyword_overlap=1,

    max_context_chars=8000

)

# ==============================================
# QUERY UNDERSTANDING
# ==============================================

def understand_query(
    state
):

    # ==========================================
    # GET ORIGINAL QUESTION
    # ==========================================

    question = state[
        "question"
    ]

    # ==========================================
    # UNDERSTAND QUERY
    # ==========================================

    result = query_understanding.understand(

        question

    )

    # ==========================================
    # STORE REWRITTEN QUERY
    # ==========================================

    state[
        "rewritten_query"
    ] = result.get(

        "rewritten_query",

        question

    )

    # ==========================================
    # STORE INTENT
    # ==========================================

    state[
        "intent"
    ] = result.get(

        "intent",

        "general_information"

    )

    # ==========================================
    # STORE ENTITIES
    # ==========================================

    state[
        "entities"
    ] = result.get(

        "entities",

        []

    )

    # ==========================================
    # STORE METADATA FILTERS
    # ==========================================

    state[
        "metadata_filters"
    ] = result.get(

        "metadata_filters",

        {}

    )

    # ==========================================
    # DEBUG INFORMATION
    # ==========================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "QUERY UNDERSTANDING"
    )

    print(
        "=" * 60
    )

    print(
        f"Original Query: "
        f"{question}"
    )

    print(
        f"Rewritten Query: "
        f"{state['rewritten_query']}"
    )

    print(
        f"Intent: "
        f"{state['intent']}"
    )

    print(
        f"Entities: "
        f"{state['entities']}"
    )

    print(
        f"Metadata Filters: "
        f"{state['metadata_filters']}"
    )

    print(
        "=" * 60
    )

    return state


# ==============================================
# CACHE CHECK
# ==============================================

def check_cache(
    state
):

    question = state[
        "question"
    ]

    cached = cache.get(
        question
    )

    if cached:

        state[
            "answer"
        ] = cached

        state[
            "cache_hit"
        ] = True

    else:

        state[
            "cache_hit"
        ] = False

    return state


# ==============================================
# RETRIEVE DOCUMENTS
# ==============================================

def retrieve_documents(
    state
):

    # ==========================================
    # SKIP IF CACHE HIT
    # ==========================================

    if state.get(
        "cache_hit",
        False
    ):

        return state

    # ==========================================
    # GET REWRITTEN QUERY
    # ==========================================

    query = state.get(

        "rewritten_query",

        state[
            "question"
        ]

    )

    # ==========================================
    # GET METADATA FILTERS
    # ==========================================

    filters = state.get(

        "metadata_filters",

        {}

    )

    # ==========================================
    # HYBRID RETRIEVAL
    # ==========================================

    docs = retriever.search(

        query=query,

        top_k=20,

        filters=filters

    )

    # ==========================================
    # STORE RETRIEVED DOCUMENTS
    # ==========================================

    state[
        "retrieved_docs"
    ] = [

        doc

        for doc, _

        in docs

    ]

    # ==========================================
    # STORE RETRIEVAL COUNT
    # ==========================================

    state[
        "retrieval_count"
    ] = len(
        docs
    )

    print(
        f"\nHybrid Candidates: "
        f"{len(docs)}"
    )

    return state


# ==============================================
# RERANK DOCUMENTS
# ==============================================

def rerank_documents(
    state
):

    # ==========================================
    # SKIP IF CACHE HIT
    # ==========================================

    if state.get(
        "cache_hit",
        False
    ):

        return state

    # ==========================================
    # GET DOCUMENTS
    # ==========================================

    documents = state.get(

        "retrieved_docs",

        []

    )

    # ==========================================
    # GET REWRITTEN QUERY
    # ==========================================

    query = state.get(

        "rewritten_query",

        state[
            "question"
        ]

    )

    # ==========================================
    # RERANK
    # ==========================================

    reranked = reranker.rerank(

        query=query,

        documents=documents,

        top_k=5

    )

    # ==========================================
    # STORE RERANKED DOCUMENTS
    # ==========================================

    state[
        "reranked_docs"
    ] = reranked

    # ==========================================
    # STORE CONTEXT COUNT
    # ==========================================

    state[
        "context_count"
    ] = len(
        reranked
    )

    print(
        f"Reranked Documents: "
        f"{len(reranked)}"
    )

    return state

# ==============================================
# BUILD REFINED CONTEXT
# ==============================================

def build_context(
    state
):

    # ==========================================
    # SKIP IF CACHE HIT
    # ==========================================

    if state.get(
        "cache_hit",
        False
    ):

        return state

    # ==========================================
    # GET RERANKED DOCUMENTS
    # ==========================================

    reranked_docs = state.get(

        "reranked_docs",

        []

    )

    # ==========================================
    # GET QUERY
    # ==========================================

    query = state.get(

        "rewritten_query",

        state[
            "question"
        ]

    )

    # ==========================================
    # REFINE CONTEXT
    # ==========================================

    refined_context = refiner.refine(

        query=query,

        documents=reranked_docs

    )

    # ==========================================
    # STORE CONTEXT
    # ==========================================

    state[
        "context"
    ] = refined_context

    # ==========================================
    # CONTEXT COUNT
    # ==========================================

    state[
        "context_count"
    ] = len(

        reranked_docs

    )

    return state


# ==============================================
# SAVE CACHE
# ==============================================

def save_cache(
    state
):

    # ==========================================
    # ONLY CACHE NEW ANSWERS
    # ==========================================

    if not state.get(

        "cache_hit",

        False

    ):

        cache.set(

            state[
                "question"
            ],

            state[
                "answer"
            ]

        )

    return state

# ==============================================
# BUILD REFINED CONTEXT
# ==============================================

def build_context(
    state
):

    # ==========================================
    # SKIP IF CACHE HIT
    # ==========================================

    if state.get(
        "cache_hit",
        False
    ):

        return state

    # ==========================================
    # GET RERANKED DOCUMENTS
    # ==========================================

    reranked_docs = state.get(

        "reranked_docs",

        []

    )

    # ==========================================
    # GET QUERY
    # ==========================================

    query = state.get(

        "rewritten_query",

        state.get(

            "question",

            ""

        )

    )

    # ==========================================
    # REFINE CONTEXT
    # ==========================================

    refined_context = refiner.refine(

        query=query,

        documents=reranked_docs

    )

    # ==========================================
    # STORE CONTEXT
    # ==========================================

    state[
        "context"
    ] = refined_context

    # ==========================================
    # UPDATE CONTEXT COUNT
    # ==========================================

    state[
        "context_count"
    ] = len(

        reranked_docs

    )

    return state



# ==============================================
# GENERATE ANSWER
# ==============================================

def generate_answer(
    state
):

    # ==========================================
    # SKIP IF CACHE HIT
    # ==========================================

    if state.get(
        "cache_hit",
        False
    ):

        return state

    # ==========================================
    # BUILD PROMPT
    # ==========================================

    prompt = build_prompt(

        question=state[
            "question"
        ],

        context=state.get(
            "context",
            ""
        )

    )

    # ==========================================
    # GENERATE ANSWER
    # ==========================================

    answer = llm.generate(
        prompt
    )

    # ==========================================
    # STORE ANSWER
    # ==========================================

    state[
        "answer"
    ] = answer

    return state