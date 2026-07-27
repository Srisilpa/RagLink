from langgraph.graph import (
    StateGraph,
    END
)

from rag.langgraph.state import (
    GraphState
)

from rag.langgraph.nodes import (
    check_cache,
    rewrite_query,
    retrieve_documents,
    rerank_documents,
    build_context,
    generate_answer,
    save_cache,
)


# ==================================================
# CREATE GRAPH
# ==================================================

builder = StateGraph(
    GraphState
)


# ==================================================
# ADD NODES
# ==================================================

builder.add_node(
    "cache",
    check_cache
)

builder.add_node(
    "rewrite",
    rewrite_query
)

builder.add_node(
    "retrieve",
    retrieve_documents
)

builder.add_node(
    "rerank",
    rerank_documents
)

builder.add_node(
    "context",
    build_context
)

builder.add_node(
    "generate",
    generate_answer
)

builder.add_node(
    "save",
    save_cache
)


# ==================================================
# ENTRY POINT
# ==================================================

builder.set_entry_point(
    "cache"
)


# ==================================================
# CACHE ROUTING
# ==================================================

def route_after_cache(
    state
):

    if state.get(
        "cache_hit",
        False
    ):

        return "save"

    return "rewrite"


builder.add_conditional_edges(

    "cache",

    route_after_cache,

    {

        "rewrite":
            "rewrite",

        "save":
            "save"

    }

)


# ==================================================
# RAG PIPELINE
# ==================================================

builder.add_edge(

    "rewrite",

    "retrieve"

)

builder.add_edge(

    "retrieve",

    "rerank"

)

builder.add_edge(

    "rerank",

    "context"

)

builder.add_edge(

    "context",

    "generate"

)

builder.add_edge(

    "generate",

    "save"

)


# ==================================================
# END
# ==================================================

builder.add_edge(

    "save",

    END

)


# ==================================================
# COMPILE GRAPH
# ==================================================

graph = builder.compile()