from rag.cache.memory_cache import (
    MemoryCache,
)

from rag.query.query_understanding import (
    QueryUnderstanding,
)

from rag.retrieval.hybrid import (
    HybridRetriever,
)

from rag.retrieval.rerank import (
    Reranker,
)

from rag.generation.prompt import (
    build_prompt,
)

from rag.generation.llm import (
    GroqLLM,
)

from rag.compression.compressor import (
    ContextCompressor,
)

from rag.refinement.context_refiner import (
    ContextRefiner,
)

from rag.query_understanding.entity_normalizer import (
    normalise_entities,
)

from rag.retrieval.retrieval_planner import (
    build_retrieval_plan,
)

from rag.generation.evidence_checker import (
    has_retrieved_context,
    build_safe_response,
)


# ============================================================
# INITIALIZE COMPONENTS
# ============================================================

cache = MemoryCache()

query_understanding = QueryUnderstanding()

retriever = HybridRetriever()

reranker = Reranker()

llm = GroqLLM()

compressor = ContextCompressor()

refiner = ContextRefiner(

    max_sentences_per_document=5,

    min_keyword_overlap=1,

    max_context_chars=8000,

)


# ============================================================
# QUERY UNDERSTANDING
# ============================================================

def understand_query(
    state,
):
    """
    Understand the original user query.

    Produces:

        rewritten_query
        intent
        raw entities
        metadata filters
    """

    # ========================================================
    # GET ORIGINAL QUESTION
    # ========================================================

    question = state[
        "question"
    ]

    # ========================================================
    # UNDERSTAND QUERY
    # ========================================================

    result = query_understanding.understand(
        question,
    )

    # ========================================================
    # STORE REWRITTEN QUERY
    # ========================================================

    state[
        "rewritten_query"
    ] = result.get(

        "rewritten_query",

        question,

    )

    # ========================================================
    # STORE INTENT
    # ========================================================

    state[
        "intent"
    ] = result.get(

        "intent",

        "general_information",

    )

    # ========================================================
    # STORE RAW ENTITIES
    # ========================================================

    state[
        "entities"
    ] = result.get(

        "entities",

        [],

    )

    # ========================================================
    # STORE EXISTING METADATA FILTERS
    #
    # Kept for backwards compatibility.
    #
    # The new retrieval planner will create the final
    # multi-domain retrieval plan.
    # ========================================================

    state[
        "metadata_filters"
    ] = result.get(

        "metadata_filters",

        {},

    )

    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    print(
        "\n"
        + "=" * 60,
    )

    print(
        "QUERY UNDERSTANDING",
    )

    print(
        "=" * 60,
    )

    print(
        f"Original Query: "
        f"{question}",
    )

    print(
        f"Rewritten Query: "
        f"{state['rewritten_query']}",
    )

    print(
        f"Intent: "
        f"{state['intent']}",
    )

    print(
        f"Raw Entities: "
        f"{state['entities']}",
    )

    print(
        f"Original Metadata Filters: "
        f"{state['metadata_filters']}",
    )

    print(
        "=" * 60,
    )

    return state


# ============================================================
# ENTITY NORMALISATION
# ============================================================

def normalise_entities_node(
    state,
):
    """
    Normalise extracted entities.

    Supports:

        ["Meridian", "AWS"]

    and:

        [
            {"name": "Meridian"},
            {"name": "AWS"}
        ]

    Unknown entities are not assigned a domain.
    """

    extracted_entities = state.get(

        "entities",

        [],

    )

    entity_mentions = []

    # ========================================================
    # EXTRACT ENTITY MENTIONS
    # ========================================================

    for entity in extracted_entities:

        # ----------------------------------------------------
        # STRING ENTITY
        # ----------------------------------------------------

        if isinstance(
            entity,
            str,
        ):

            entity_mentions.append(
                entity,
            )

        # ----------------------------------------------------
        # DICTIONARY ENTITY
        # ----------------------------------------------------

        elif isinstance(
            entity,
            dict,
        ):

            name = (

                entity.get(
                    "name",
                )

                or entity.get(
                    "entity",
                )

                or entity.get(
                    "text",
                )

                or entity.get(
                    "mention",
                )

                or entity.get(
                    "canonical_name",
                )

            )

            if name:

                entity_mentions.append(
                    name,
                )

    # ========================================================
    # NORMALISE
    # ========================================================

    normalised = normalise_entities(
        entity_mentions,
    )

    # ========================================================
    # STORE NORMALISED ENTITIES
    # ========================================================

    state[
        "entities"
    ] = normalised

    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "\n"
        + "=" * 60,
    )

    print(
        "ENTITY NORMALISATION",
    )

    print(
        "=" * 60,
    )

    print(
        f"Original Entities: "
        f"{entity_mentions}",
    )

    print(
        f"Normalised Entities: "
        f"{normalised}",
    )

    print(
        "=" * 60,
    )

    return state


# ============================================================
# RETRIEVAL PLANNING
# ============================================================

def retrieval_planning_node(
    state,
):
    """
    Build a multi-domain-aware retrieval plan.
    """

    query = (

        state.get(
            "rewritten_query",
        )

        or state.get(
            "question",
            "",
        )

    )

    entities = state.get(

        "entities",

        [],

    )

    retrieval_plan = build_retrieval_plan(

        query=query,

        entities=entities,

    )

    # ========================================================
    # STORE RETRIEVAL PLAN
    # ========================================================

    state[
        "retrieval_plan"
    ] = retrieval_plan

    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "\n"
        + "=" * 60,
    )

    print(
        "RETRIEVAL PLANNING",
    )

    print(
        "=" * 60,
    )

    print(
        f"Query: "
        f"{query}",
    )

    print(
        f"Entities: "
        f"{retrieval_plan.get('entities', [])}",
    )

    print(
        f"Document Types: "
        f"{retrieval_plan.get('document_types', [])}",
    )

    print(
        f"Use Metadata Filter: "
        f"{retrieval_plan.get('use_metadata_filter', False)}",
    )

    print(
        "=" * 60,
    )

    return state


# ============================================================
# CACHE CHECK
# ============================================================

def check_cache(
    state,
):
    """
    Check whether the original question is already cached.
    """

    question = state[
        "question"
    ]

    cached = cache.get(
        question,
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


# ============================================================
# RETRIEVE DOCUMENTS
# ============================================================

def retrieve_documents(
    state,
):
    """
    Retrieve documents using the retrieval plan.

    Important:

        [] document types
            -> no hard metadata filter

        ["project"]
            -> project domain

        ["project", "infrastructure"]
            -> multi-domain retrieval

    The HybridRetriever must support the corresponding
    filter structure.
    """

    # ========================================================
    # SKIP IF CACHE HIT
    # ========================================================

    if state.get(
        "cache_hit",
        False,
    ):

        return state

    # ========================================================
    # GET QUERY
    # ========================================================

    query = (

        state.get(
            "rewritten_query",
        )

        or state.get(
            "question",
            "",
        )

    )

    # ========================================================
    # GET RETRIEVAL PLAN
    # ========================================================

    retrieval_plan = state.get(

        "retrieval_plan",

        {},

    )

    # ========================================================
    # GET DOCUMENT TYPES
    # ========================================================

    document_types = retrieval_plan.get(

        "document_types",

        [],

    )

    # ========================================================
    # BUILD FILTERS
    # ========================================================

    filters = {}

    if document_types:

        filters = {

            "document_type": document_types,

        }

    # ========================================================
    # DEBUG RETRIEVAL PLAN
    # ========================================================

    print(
        "\n"
        + "=" * 60,
    )

    print(
        "RETRIEVAL EXECUTION",
    )

    print(
        "=" * 60,
    )

    print(
        f"Query: "
        f"{query}",
    )

    print(
        f"Entities: "
        f"{retrieval_plan.get('entities', [])}",
    )

    print(
        f"Document Types: "
        f"{document_types}",
    )

    print(
        f"Filters: "
        f"{filters}",
    )

    print(
        "=" * 60,
    )

    # ========================================================
    # HYBRID RETRIEVAL
    # ========================================================

    docs = retriever.search(

        query=query,

        top_k=20,

        filters=filters,

    )

    # ========================================================
    # STORE DOCUMENTS
    # ========================================================

    state[
        "retrieved_docs"
    ] = [

        doc

        for doc, _

        in docs

    ]

    # ========================================================
    # STORE COUNT
    # ========================================================

    state[
        "retrieval_count"
    ] = len(
        docs
    )

    print(
        f"\nHybrid Candidates: "
        f"{len(docs)}",
    )

    return state


# ============================================================
# RERANK DOCUMENTS
# ============================================================

def rerank_documents(
    state,
):
    """
    Rerank retrieved documents using the cross encoder.
    """

    # ========================================================
    # SKIP IF CACHE HIT
    # ========================================================

    if state.get(
        "cache_hit",
        False,
    ):

        return state

    # ========================================================
    # GET DOCUMENTS
    # ========================================================

    documents = state.get(

        "retrieved_docs",

        [],

    )

    # ========================================================
    # GET QUERY
    # ========================================================

    query = (

        state.get(
            "rewritten_query",
        )

        or state.get(
            "question",
            "",
        )

    )

    # ========================================================
    # RERANK
    # ========================================================

    reranked = reranker.rerank(

        query=query,

        documents=documents,

        top_k=5,

    )

    # ========================================================
    # STORE RERANKED DOCUMENTS
    # ========================================================

    state[
        "reranked_docs"
    ] = reranked

    # ========================================================
    # STORE COUNT
    # ========================================================

    state[
        "context_count"
    ] = len(
        reranked
    )

    print(
        f"Reranked Documents: "
        f"{len(reranked)}",
    )

    return state


# ============================================================
# BUILD REFINED CONTEXT
# ============================================================

def build_context(
    state,
):
    """
    Build the final refined context from reranked documents.
    """

    # ========================================================
    # SKIP IF CACHE HIT
    # ========================================================

    if state.get(
        "cache_hit",
        False,
    ):

        return state

    # ========================================================
    # GET RERANKED DOCUMENTS
    # ========================================================

    reranked_docs = state.get(

        "reranked_docs",

        [],

    )

    # ========================================================
    # GET QUERY
    # ========================================================

    query = (

        state.get(
            "rewritten_query",
        )

        or state.get(
            "question",
            "",
        )

    )

    # ========================================================
    # REFINE CONTEXT
    # ========================================================

    refined_context = refiner.refine(

        query=query,

        documents=reranked_docs,

    )

    # ========================================================
    # STORE CONTEXT
    # ========================================================

    state[
        "context"
    ] = refined_context

    # ========================================================
    # UPDATE CONTEXT COUNT
    # ========================================================

    state[
        "context_count"
    ] = len(
        reranked_docs
    )

    return state


# ============================================================
# EVIDENCE CHECK
# ============================================================

def evidence_check_node(
    state,
):
    """
    Perform a basic evidence availability check.

    This checks whether the context contains usable text.

    Note:
    This is NOT yet a semantic answer-verification step.
    """

    context = state.get(

        "context",

        "",

    )

    # ContextRefiner currently returns a string,
    # so convert it to a list for the checker.

    contexts = []

    if isinstance(
        context,
        str,
    ):

        if context.strip():

            contexts = [
                context
            ]

    elif isinstance(
        context,
        list,
    ):

        contexts = context

    sufficient = has_retrieved_context(
        contexts,
    )

    state[
        "evidence_sufficient"
    ] = sufficient

    print(
        "\n"
        + "=" * 60,
    )

    print(
        "EVIDENCE CHECK",
    )

    print(
        "=" * 60,
    )

    print(
        f"Evidence Sufficient: "
        f"{sufficient}",
    )

    print(
        "=" * 60,
    )

    return state


# ============================================================
# SAFE RESPONSE
# ============================================================

def safe_response(
    state,
):
    """
    Generate a safe response when usable evidence
    is unavailable.
    """

    if state.get(
        "cache_hit",
        False,
    ):

        return state

    state[
        "answer"
    ] = build_safe_response()

    return state


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    state,
):
    """
    Generate a grounded answer using the final context.
    """

    # ========================================================
    # SKIP IF CACHE HIT
    # ========================================================

    if state.get(
        "cache_hit",
        False,
    ):

        return state

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    prompt = build_prompt(

        question=state[
            "question"
        ],

        context=state.get(

            "context",

            "",

        ),

    )

    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    answer = llm.generate(
        prompt,
    )

    # ========================================================
    # STORE ANSWER
    # ========================================================

    state[
        "answer"
    ] = answer

    return state


# ============================================================
# SAVE CACHE
# ============================================================

def save_cache(
    state,
):
    """
    Cache newly generated answers.

    Cached answers are not written again on cache hits.
    """

    if not state.get(

        "cache_hit",

        False,

    ):

        cache.set(

            state[
                "question"
            ],

            state[
                "answer"
            ],

        )

    return state