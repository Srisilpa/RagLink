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
    # QUERY UNDERSTANDING
    # ==========================================

    # Rewritten query used for retrieval
    rewritten_query: str

    # Detected intent
    # Example:
    # database_information
    # policy_information
    # technology_information

    intent: str

    # Important entities extracted
    # Example:
    # ["Project Meridian"]
    # ["Series Tech Limited", "London"]

    entities: List[str]

    # ==========================================
    # METADATA FILTERS
    # ==========================================

    # Example:
    # {"document_type": "project"}
    #
    # or:
    # {"document_type": "company"}

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