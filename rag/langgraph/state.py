from typing import (
    TypedDict,
    List,
    Dict,
    Any
)

from langchain_core.documents import Document


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
    # QUERY INTENT
    # ==========================================

    intent: str

    # ==========================================
    # EXTRACTED ENTITIES
    # ==========================================

    entities: List[str]

    # ==========================================
    # METADATA FILTERS
    #
    # Example:
    #
    # {
    #     "document_type": ["project", "company"]
    # }
    # ==========================================

    metadata_filters: Dict[str, Any]

    # ==========================================
    # RETRIEVED DOCUMENTS
    # ==========================================

    retrieved_docs: List[Document]

    # ==========================================
    # RERANKED DOCUMENTS
    #
    # [
    #     (Document, score),
    #     ...
    # ]
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
    # CONTEXT COUNT
    # ==========================================

    context_count: int

    # ==========================================
    # LATENCY
    # ==========================================

    latency: float