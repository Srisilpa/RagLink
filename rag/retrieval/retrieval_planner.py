"""
Retrieval planning for RAGLink.

Builds an intelligent retrieval plan using:

1. Normalized entities
2. Query Understanding output
3. Intent
4. Expanded queries
5. Metadata filters

This planner determines:

• Search queries
• Metadata filters
• Retrieval depth
• Retrieval strategy
"""

from typing import Dict, List

from rag.query_understanding.entity_normalizer import (
    normalise_entity,
)


# ============================================================
# DOMAIN → DOCUMENT TYPE
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

    # Projects
    "project meridian",
    "meridian project",

    # Company
    "series tech limited",
    "series tech",

    # Infrastructure
    "amazon web services",
    "aws",
    "microsoft azure",
    "azure",

}


# ============================================================
# DETECT ENTITIES DIRECTLY FROM QUERY
# ============================================================

def detect_known_entities_from_query(
    query: str,
) -> List[str]:

    if not query:
        return []

    query = query.lower()

    detected = []

    for mention in sorted(
        KNOWN_ENTITY_MENTIONS,
        key=len,
        reverse=True,
    ):

        if mention in query:

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
) -> List[Dict]:

    merged = []


    # Existing Query Understanding entities

    if entities:

        for entity in entities:

            if isinstance(
                entity,
                dict
            ):

                merged.append(
                    entity
                )



    # Detect known entities

    detected_entities = detect_known_entities_from_query(
        query
    )


    for mention in detected_entities:

        info = normalise_entity(
            mention
        )


        if info is None:

            continue


        merged.append(

            {
                "mention":
                    mention,

                "canonical_name":
                    info.canonical_name,

                "entity_type":
                    info.entity_type,
            }

        )



    # Remove duplicates

    unique = []

    seen = set()


    for entity in merged:

        key = (

            entity.get(
                "canonical_name"
            ),

            entity.get(
                "entity_type"
            )

        )


        if key in seen:

            continue


        seen.add(key)


        unique.append(
            entity
        )


    return unique



# ============================================================
# BUILD METADATA FILTERS
# ============================================================

def build_metadata_filters(
    entities: List[Dict],
) -> Dict:
    """
    Creates metadata filters compatible with Chroma.

    Existing Chroma metadata:

    {
        document_type,
        file_name,
        source,
        document_id
    }

    """


    filters = {}


    document_types = set()

    file_names = []

    companies = []

    technologies = []



    for entity in entities:


        entity_type = entity.get(
            "entity_type",
            ""
        )


        canonical_name = entity.get(
            "canonical_name",
            ""
        )



        document_type = DOMAIN_TO_DOCUMENT_TYPE.get(
            entity_type
        )


        if document_type:

            document_types.add(
                document_type
            )



                # ----------------------------------------
        # PROJECT FILTER
        # ----------------------------------------

        if entity_type == "project":

            project_name = canonical_name.replace(
                " ",
                "_"
            )

            file_names.append(
                f"{project_name}_Comprehensive_Technical_Specification.pdf"
            )

        # ----------------------------------------
        # COMPANY FILTER
        # ----------------------------------------

        elif entity_type == "company":

            companies.append(
                canonical_name
            )



        # ----------------------------------------
        # INFRASTRUCTURE FILTER
        # ----------------------------------------

        elif entity_type == "infrastructure":

            technologies.append(
                canonical_name
            )



    if document_types:

        filters["document_type"] = list(
            document_types
        )



    if file_names:

        filters["file_name"] = list(
            set(file_names)
        )



    if companies:

        filters["company"] = list(
            set(companies)
        )



    if technologies:

        filters["technology"] = list(
            set(technologies)
        )


    return filters



# ============================================================
# BUILD SEARCH QUERIES
# ============================================================

def _build_search_queries(
    query: str,
    rewritten_query: str,
    expanded_queries: List[str],
    canonical_entities: List[str],
) -> List[str]:


    queries = []


    for q in (
        query,
        rewritten_query,
    ):


        if q and q not in queries:

            queries.append(
                q
            )



    for q in expanded_queries or []:


        q = q.strip()


        if q and q not in queries:

            queries.append(
                q
            )



    for entity in canonical_entities:


        if entity not in queries:

            queries.append(
                entity
            )


    return queries



# ============================================================
# RETRIEVAL DEPTH
# ============================================================

def _determine_top_k(
    intent: str,
    entity_count: int,
) -> int:


    top_k = 15


    if intent in (

        "summary",

        "comparison",

        "architecture",

        "tech_stack",

    ):

        top_k = 25



    elif intent in (

        "procedure",

        "policy",

    ):

        top_k = 20



    if entity_count >= 3:

        top_k += 5



    return min(
        top_k,
        30
    )



# ============================================================
# PUBLIC RETRIEVAL PLANNER
# ============================================================

def build_retrieval_plan(
    query: str,
    rewritten_query: str,
    entities: List[Dict],
    expanded_queries: List[str],
    intent: str,
):


    merged_entities = merge_entity_mentions(
        query,
        entities
    )



    canonical_entities = []



    for entity in merged_entities:


        name = (

            entity.get(
                "canonical_name"
            )

            or

            entity.get(
                "mention"
            )

        )


        if name:

            canonical_entities.append(
                name
            )



    search_queries = _build_search_queries(

        query=query,

        rewritten_query=rewritten_query,

        expanded_queries=expanded_queries,

        canonical_entities=canonical_entities,

    )



    metadata_filters = build_metadata_filters(
        merged_entities
    )



    document_types = metadata_filters.get(
        "document_type",
        []
    )



    top_k = _determine_top_k(

        intent,

        len(canonical_entities)

    )



    return {


        "search_queries":
            search_queries,


        "document_types":
            document_types,


        "metadata_filters":
            metadata_filters,


        "entities":
            canonical_entities,


        "top_k":
            top_k,


    }