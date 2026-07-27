from typing import (
    TypedDict,
    List,
    Dict
)

from langchain_core.documents import (
    Document
)


class GraphState(
    TypedDict,
    total=False
):

    # ==========================================
    # ORIGINAL USER QUERY
    # ==========================================

    question: str

    # ==========================================
    # REWRITTEN QUERY
    # ==========================================

    rewritten_query: str

    # ==========================================
    # METADATA FILTERS
    # ==========================================

    metadata_filters: Dict

    # ==========================================
    # RETRIEVED DOCUMENTS
    # ==========================================

    retrieved_docs: List[
        Document
    ]

    # ==========================================
    # RERANKED DOCUMENTS
    #
    # (Document, relevance_score)
    # ==========================================

    reranked_docs: List

    # ==========================================
    # FINAL CONTEXT
    # ==========================================

    context: str

    # ==========================================
    # GENERATED ANSWER
    # ==========================================

    answer: str

    # ==========================================
    # CACHE INFORMATION
    # ==========================================

    cache_hit: bool

    # ==========================================
    # RETRIEVAL METADATA
    # ==========================================

    retrieval_count: int

    # ==========================================
    # FINAL CONTEXT COUNT
    # ==========================================

    context_count: int

    # ==========================================
    # LATENCY INFORMATION
    # ==========================================

    latency: float