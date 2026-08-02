from rag.cache.memory_cache import MemoryCache


from rag.query_understanding.query_understanding import (
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
    verify_answer_grounding,
)


from rag.generation.citation import (
    build_sources,
    append_sources,
)


from rag.tools.query_router import (
    classify_query,
)


from rag.tools.calculator import (
    calculator_tool,
)


from rag.tools.date import (
    current_date_tool,
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
# CACHE CHECK
# ============================================================

def check_cache(state):

    question = state["question"]


    cached_answer = cache.get(
        question
    )


    if cached_answer:


        print("\nCACHE HIT")


        state["cache_hit"] = True

        state["answer"] = cached_answer



    else:


        print("\nCACHE MISS")


        state["cache_hit"] = False



    return state




# ============================================================
# QUERY ROUTER
# ============================================================

def query_router_node(state):


    question = state["question"]


    query_type = classify_query(
        question
    )


    state["query_type"] = query_type



    print("\nQUERY ROUTER")
    print(
        "Route:",
        query_type
    )


    return state


# ============================================================
# QUERY UNDERSTANDING
# ============================================================

def understand_query(state):
    """
    Performs:

    - Query rewriting
    - Intent detection
    - Entity extraction
    - Query expansion
    """


    question = state["question"]


    result = query_understanding.understand(
        question
    )


    state["rewritten_query"] = result.get(
        "rewritten_query",
        question
    )


    state["intent"] = result.get(
        "intent",
        "general_information"
    )


    state["entities"] = result.get(
        "entities",
        []
    )


    state["expanded_queries"] = result.get(
        "expanded_queries",
        [
            state["rewritten_query"]
        ]
    )


    state["metadata_filters"] = result.get(
        "metadata_filters",
        {}
    )


    print("\n" + "=" * 60)
    print("QUERY UNDERSTANDING")
    print("=" * 60)

    print(
        "Original:",
        question
    )

    print(
        "Rewrite:",
        state["rewritten_query"]
    )

    print(
        "Intent:",
        state["intent"]
    )

    print(
        "Entities:",
        state["entities"]
    )

    print(
        "Expanded:",
        state["expanded_queries"]
    )

    print("=" * 60)


    return state





# ============================================================
# ENTITY NORMALISATION
# ============================================================

def normalise_entities_node(state):
    """
    Converts extracted entities into
    canonical entity dictionaries.
    """


    raw_entities = state.get(
        "entities",
        []
    )


    mentions = []


    for entity in raw_entities:


        if isinstance(
            entity,
            str
        ):

            mentions.append(
                entity
            )


        elif isinstance(
            entity,
            dict
        ):


            value = (

                entity.get(
                    "canonical_name"
                )

                or

                entity.get(
                    "mention"
                )

                or

                entity.get(
                    "name"
                )

            )


            if value:

                mentions.append(
                    value
                )



    normalized = normalise_entities(
        mentions
    )


    state["entities"] = normalized



    print("\n" + "=" * 60)
    print("ENTITY NORMALISATION")
    print("=" * 60)

    print(
        normalized
    )

    print("=" * 60)



    return state





# ============================================================
# RETRIEVAL PLANNING
# ============================================================

def retrieval_planning_node(state):
    """
    Creates intelligent retrieval plan.

    Uses:

    - original query
    - rewritten query
    - entities
    - intent
    - expanded queries
    """


    original_query = state.get(
        "question",
        ""
    )


    rewritten_query = state.get(
        "rewritten_query",
        original_query
    )


    entities = state.get(
        "entities",
        []
    )


    expanded_queries = state.get(
        "expanded_queries",
        []
    )


    intent = state.get(
        "intent",
        "general_information"
    )



    retrieval_plan = build_retrieval_plan(

        query=original_query,

        rewritten_query=rewritten_query,

        entities=entities,

        expanded_queries=expanded_queries,

        intent=intent,

    )



    state["retrieval_plan"] = retrieval_plan



    # Store planner outputs

    state["search_queries"] = retrieval_plan.get(
        "search_queries",
        []
    )


    state["document_types"] = retrieval_plan.get(
        "document_types",
        []
    )


    state["metadata_filters"] = retrieval_plan.get(
        "metadata_filters",
        {}
    )


    state["retrieval_strategy"] = "hybrid"



    print("\n" + "=" * 60)
    print("RETRIEVAL PLAN")
    print("=" * 60)

    print(
        retrieval_plan
    )

    print("=" * 60)



    return state


# ============================================================
# RETRIEVE DOCUMENTS
# ============================================================

def retrieve_documents(state):
    """
    Hybrid retrieval:

    - Semantic Search
    - BM25
    - Metadata filtering
    """


    if state.get(
        "cache_hit",
        False
    ):

        return state



    plan = state.get(
        "retrieval_plan",
        {}
    )


    queries = plan.get(
        "search_queries",
        [
            state.get(
                "rewritten_query",
                state["question"]
            )
        ]
    )


    filters = plan.get(
        "metadata_filters",
        {}
    )


    top_k = plan.get(
        "top_k",
        20
    )


    print("\n" + "=" * 60)
    print("RETRIEVAL")
    print("=" * 60)


    print(
        "Queries:",
        queries
    )


    print(
        "Filters:",
        filters
    )


    print(
        "Top K:",
        top_k
    )



    results = retriever.search_multiple(

        queries=queries,

        top_k=top_k,

        filters=filters,

    )



    state["retrieved_results"] = results



    state["retrieved_docs"] = [

        doc

        for doc, score

        in results

    ]



    state["retrieval_scores"] = [

        score

        for doc, score

        in results

    ]



    state["retrieval_count"] = len(
        results
    )



    print(
        f"Retrieved Documents: {len(results)}"
    )


    print("=" * 60)



    return state





# ============================================================
# RERANK DOCUMENTS
# ============================================================

def rerank_documents(state):
    """
    Cross Encoder reranking.
    """


    if state.get(
        "cache_hit",
        False
    ):

        return state



    query = state.get(
        "rewritten_query",
        state["question"]
    )


    documents = state.get(
        "retrieved_docs",
        []
    )


    if not documents:


        state["reranked_docs"] = []

        return state




    reranked = reranker.rerank(

        query=query,

        documents=documents,

        top_k=5,

    )



    state["reranked_docs"] = reranked



    print("\n" + "=" * 60)
    print("RERANKING")
    print("=" * 60)


    print(
        f"Final Documents: {len(reranked)}"
    )


    print("=" * 60)



    return state





# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(state):
    """
    Builds final context using:

    - Context compression
    - Context refinement
    """


    if state.get(
        "cache_hit",
        False
    ):

        return state



    query = state.get(
        "rewritten_query",
        state["question"]
    )



    documents = state.get(
        "reranked_docs",
        []
    )



    if not documents:


        state["context"] = ""

        state["context_count"] = 0

        return state




    print("\n" + "=" * 60)
    print("CONTEXT BUILDING")
    print("=" * 60)




    # -----------------------------
    # Compression
    # -----------------------------

    compressed = compressor.compress(

        query=query,

        documents=documents,

    )




    # -----------------------------
    # Refinement
    # -----------------------------

    refined = refiner.refine(

        query=query,

        documents=compressed,

    )



    state["compressed_docs"] = compressed


    state["context"] = refined


    state["context_count"] = len(
        compressed
    )



    print(
        f"Compressed Docs: {len(compressed)}"
    )


    print(
        f"Context Length: {len(refined)}"
    )


    print("=" * 60)



    return state


# ============================================================
# EVIDENCE CHECK
# ============================================================

def evidence_check_node(state):
    """
    Checks whether retrieved context
    is sufficient for generation.
    """


    if state.get(
        "cache_hit",
        False
    ):

        return state



    context = state.get(
        "context",
        ""
    )


    contexts = []


    if isinstance(
        context,
        str
    ):

        if context.strip():

            contexts.append(
                context
            )


    elif isinstance(
        context,
        list
    ):

        contexts = context



    result = has_retrieved_context(
        contexts
    )


    state["evidence_sufficient"] = result



    print("\n" + "=" * 60)
    print("EVIDENCE CHECK")
    print("=" * 60)

    print(
        "Evidence:",
        result
    )

    print("=" * 60)



    return state





# ============================================================
# SAFE RESPONSE
# ============================================================

def safe_response(state):
    """
    Generates fallback when
    evidence is unavailable.
    """


    if state.get(
        "evidence_sufficient",
        True
    ):

        return state



    state["answer"] = build_safe_response()


    state["context_count"] = 0


    print(
        "\nSAFE RESPONSE"
    )

    print(
        state["answer"]
    )


    return state





# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(state):
    """
    Generates final answer using context.
    """


    if state.get(
        "cache_hit",
        False
    ):

        return state



    question = state["question"]


    context = state.get(
        "context",
        ""
    )



    if not context:

        state["answer"] = build_safe_response()

        return state



    print("\n" + "=" * 60)
    print("ANSWER GENERATION")
    print("=" * 60)



    prompt = build_prompt(

        question=question,

        context=context,

    )



    answer = llm.generate(
        prompt
    ).strip()



    fallback = (
        "I couldn't find that information "
        "in the company knowledge base."
    )



    if not answer:

        answer = fallback



    grounding_result = verify_answer_grounding(

        answer=answer,

        context=context,

    )


    state["grounding_score"] = grounding_result



    if grounding_result is False:

        answer = fallback



    state["answer"] = answer



    print(
        "\nAnswer:"
    )

    print(
        answer
    )


    print("=" * 60)



    return state





# ============================================================
# BUILD CITATIONS
# ============================================================

def add_citations(state):
    """
    Adds source citations.
    """


    if state.get(
        "cache_hit",
        False
    ):

        return state



    documents = state.get(
        "reranked_docs",
        []
    )



    sources = build_sources(
        documents
    )


    state["sources"] = sources



    if state.get(
        "answer"
    ):


        state["answer"] = append_sources(

            answer=state["answer"],

            sources=sources,

        )



    return state





# ============================================================
# SAVE CACHE
# ============================================================

def save_cache(state):
    """
    Stores generated answer.
    """


    if state.get(
        "cache_hit",
        False
    ):

        return state



    answer = state.get(
        "answer"
    )


    if answer:


        cache.set(

            state["question"],

            answer,

        )


        print(
            "\nCACHE SAVED"
        )



    return state





# ============================================================
# TOOL HANDLER
# ============================================================

def tool_handler(state):
    """
    Handles tool queries.

    Supports:

    - calculator
    - date
    - time
    """


    question = state["question"]


    query_type = state.get(
        "query_type",
        classify_query(question)
    )



    try:


        if query_type == "calculator":


            answer = calculator_tool(
                question
            )



        elif query_type == "date":


            answer = current_date_tool()



        elif query_type == "time":


            from rag.tools.time import (
                current_time_tool,
            )


            answer = current_time_tool()



        else:


            answer = (
                "I could not find a suitable tool "
                "for this query."
            )



    except Exception as e:


        answer = (
            f"Tool Error: {e}"
        )



    state["answer"] = answer



    print(
        "\nTOOL ANSWER:"
    )

    print(
        answer
    )



    return state