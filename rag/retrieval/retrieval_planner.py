"""
Retrieval planning for RAGLink.

This module builds a retrieval plan using BOTH:

1. Entities extracted by QueryUnderstanding
2. Known entity mentions directly detected in the query

This is important because LLM-based entity extraction
can miss entities.

Example:

    Query:
        "What AWS and Azure services does Project Meridian use?"

Even if QueryUnderstanding returns:

    ["Project Meridian"]

The planner can still detect:

    AWS
    Azure

directly from the query.

Therefore:

    Project Meridian -> project
    AWS              -> infrastructure
    Azure            -> infrastructure

Final retrieval plan:

    document_types = [
        "infrastructure",
        "project"
    ]
"""

from typing import Dict, List

from rag.query_understanding.entity_normalizer import (
    normalise_entity,
)


# ============================================================
# DOMAIN MAPPING
# ============================================================

DOMAIN_TO_DOCUMENT_TYPE = {

    "project": "project",

    "company": "company",

    "infrastructure": "infrastructure",

}


# ============================================================
# KNOWN ENTITY MENTIONS
# ============================================================

KNOWN_ENTITY_MENTIONS = {

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    "project meridian",

    "meridian",

    # --------------------------------------------------------
    # COMPANY
    # --------------------------------------------------------

    "series tech limited",

    "series tech",

    # --------------------------------------------------------
    # INFRASTRUCTURE
    # --------------------------------------------------------

    "aws",

    "amazon web services",

    "azure",

    "microsoft azure",

}


# ============================================================
# EXTRACT ENTITY MENTIONS FROM QUERY
# ============================================================

def detect_known_entities_from_query(
    query: str,
) -> List[str]:
    """
    Detect known entity mentions directly from the query.

    This is deterministic and does not depend on the LLM.

    Example:

        Query:
            "What AWS and Azure services does Project Meridian use?"

        Returns:

            [
                "Project Meridian",
                "AWS",
                "Azure"
            ]
    """

    if not query:

        return []

    query_lower = query.lower()

    detected = []

    # ========================================================
    # LONGEST MATCH FIRST
    #
    # This prevents:
    #
    # "amazon web services"
    #
    # from being treated differently from:
    #
    # "aws"
    # ========================================================

    sorted_mentions = sorted(

        KNOWN_ENTITY_MENTIONS,

        key=len,

        reverse=True,

    )

    for mention in sorted_mentions:

        if mention in query_lower:

            detected.append(
                mention
            )

    return detected


# ============================================================
# MERGE ENTITY SOURCES
# ============================================================

def merge_entity_mentions(
    query: str,
    entities: List[Dict],
) -> List[str]:
    """
    Merge:

        1. LLM-extracted entities
        2. Deterministically detected known entities

    Duplicate entities are removed.
    """

    merged = []

    # ========================================================
    # ADD LLM ENTITIES
    # ========================================================

    for entity in entities:

        if not isinstance(
            entity,
            dict,
        ):

            continue

        canonical_name = entity.get(
            "canonical_name"
        )

        mention = entity.get(
            "mention"
        )

        if canonical_name:

            merged.append(
                canonical_name
            )

        elif mention:

            merged.append(
                mention
            )

    # ========================================================
    # ADD DIRECTLY DETECTED ENTITIES
    # ========================================================

    detected = detect_known_entities_from_query(
        query
    )

    merged.extend(
        detected
    )

    # ========================================================
    # NORMALISE + DEDUPLICATE
    # ========================================================

    canonical_entities = []

    seen = set()

    for entity in merged:

        info = normalise_entity(
            entity
        )

        if info is None:

            continue

        canonical_name = (
            info.canonical_name
        )

        key = canonical_name.lower()

        if key in seen:

            continue

        seen.add(
            key
        )

        canonical_entities.append(
            canonical_name
        )

    return canonical_entities


# ============================================================
# BUILD RETRIEVAL PLAN
# ============================================================

def build_retrieval_plan(
    query: str,
    entities: List[Dict],
) -> Dict:
    """
    Build a multi-domain-aware retrieval plan.

    Domain detection is based on:

        - LLM extracted entities
        - Direct known entity detection

    Examples:

        Project Meridian

        ->
        document_types = ["project"]


        Project Meridian + AWS + Azure

        ->
        document_types = [
            "infrastructure",
            "project"
        ]


        Unknown query

        ->
        document_types = []

        No hard metadata filtering is applied.
    """

    # ========================================================
    # MERGE ENTITY INFORMATION
    # ========================================================

    canonical_entities = merge_entity_mentions(

        query=query,

        entities=entities,

    )

    # ========================================================
    # DETECT DOMAINS
    # ========================================================

    document_types = set()

    for canonical_entity in canonical_entities:

        info = normalise_entity(
            canonical_entity
        )

        if info is None:

            continue

        entity_type = info.entity_type

        document_type = (
            DOMAIN_TO_DOCUMENT_TYPE.get(
                entity_type
            )
        )

        if document_type:

            document_types.add(
                document_type
            )

    # ========================================================
    # SORT FOR DETERMINISTIC OUTPUT
    # ========================================================

    document_types = sorted(
        document_types
    )

    # ========================================================
    # BUILD FINAL PLAN
    # ========================================================

    return {

        "query": query,

        "entities": canonical_entities,

        "document_types": document_types,

        "use_metadata_filter": bool(
            document_types
        ),

    }