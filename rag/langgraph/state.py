from typing import (
    TypedDict,
    List,
    Dict,
    Any,
)

from langchain_core.documents import (
    Document,
)


class GraphState(
    TypedDict,
    total=False,
):

    # ========================================================
    # ORIGINAL USER QUERY
    # ========================================================

    question: str

    # ========================================================
    # REWRITTEN QUERY
    # ========================================================

    rewritten_query: str

    # ========================================================
    # QUERY INTENT
    # ========================================================

    intent: str

    # ========================================================
    # EXTRACTED AND NORMALISED ENTITIES
    #
    # Example:
    #
    # [
    #     {
    #         "mention": "Meridian",
    #         "canonical_name": "Project Meridian",
    #         "entity_type": "project"
    #     }
    # ]
    # ========================================================

    entities: List[
        Dict[str, Any]
    ]

    # ========================================================
    # RETRIEVAL PLAN
    #
    # Example:
    #
    # {
    #     "query": "...",
    #     "entities": [
    #         "Project Meridian",
    #         "AWS",
    #         "Azure"
    #     ],
    #     "document_types": [
    #         "infrastructure",
    #         "project"
    #     ],
    #     "use_metadata_filter": True
    # }
    # ========================================================

    retrieval_plan: Dict[
        str,
        Any,
    ]

    # ========================================================
    # METADATA FILTERS
    #
    # Kept for compatibility with the existing
    # query understanding pipeline.
    # ========================================================

    metadata_filters: Dict[
        str,
        Any,
    ]

    # ========================================================
    # MULTI-INTENT QUERIES
    # ========================================================

    sub_queries: List[
        Dict[str, Any]
    ]

    # ========================================================
    # RETRIEVED DOCUMENTS
    # ========================================================

    retrieved_docs: List[
        Document
    ]

    # ========================================================
    # RERANKED DOCUMENTS
    #
    # Typically:
    #
    # [
    #     (Document, relevance_score)
    # ]
    # ========================================================

    reranked_docs: List

    # ========================================================
    # FINAL CONTEXT
    # ========================================================

    context: str

    # ========================================================
    # EVIDENCE STATUS
    # ========================================================

    evidence_sufficient: bool

    # ========================================================
    # GENERATED ANSWER
    # ========================================================

    answer: str

    # ========================================================
    # CACHE INFORMATION
    # ========================================================

    cache_hit: bool

    # ========================================================
    # RETRIEVAL METADATA
    # ========================================================

    retrieval_count: int

    # ========================================================
    # FINAL CONTEXT COUNT
    # ========================================================

    context_count: int

    # ========================================================
    # LATENCY INFORMATION
    # ========================================================

    latency: float