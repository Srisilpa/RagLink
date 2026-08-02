from langgraph.graph import (
    StateGraph,
    END,
)

from rag.langgraph.state import GraphState


from rag.langgraph.nodes import (

    check_cache,

    query_router_node,

    understand_query,

    normalise_entities_node,

    retrieval_planning_node,

    retrieve_documents,

    rerank_documents,

    build_context,

    evidence_check_node,

    safe_response,

    generate_answer,

    add_citations,

    save_cache,

    tool_handler,

    chat_handler,

)



# ============================================================
# ROUTERS
# ============================================================


def cache_router(state):

    if state.get(
        "cache_hit",
        False
    ):

        return "cached"


    return "continue"




def route_query(state):

    query_type = state.get(
        "query_type",
        "rag"
    )


    if query_type == "rag":

        return "rag"


    elif query_type == "chat":

        return "chat"


    else:

        return "tool"




def evidence_router(state):

    if state.get(
        "evidence_sufficient",
        False
    ):

        return "generate"


    return "safe"





# ============================================================
# CREATE GRAPH
# ============================================================


builder = StateGraph(
    GraphState
)





# ============================================================
# ADD NODES
# ============================================================


builder.add_node(
    "cache",
    check_cache
)


builder.add_node(
    "query_router",
    query_router_node
)


builder.add_node(
    "understand",
    understand_query
)


builder.add_node(
    "normalise_entities",
    normalise_entities_node
)


builder.add_node(
    "retrieval_planning",
    retrieval_planning_node
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
    "evidence_check",
    evidence_check_node
)


builder.add_node(
    "safe_response",
    safe_response
)


builder.add_node(
    "generate",
    generate_answer
)


builder.add_node(
    "citations",
    add_citations
)


builder.add_node(
    "tool_handler",
    tool_handler
)


builder.add_node(
    "chat_handler",
    chat_handler
)


builder.add_node(
    "save",
    save_cache
)





# ============================================================
# ENTRY POINT
# ============================================================


builder.set_entry_point(
    "cache"
)





# ============================================================
# CACHE ROUTING
# ============================================================


builder.add_conditional_edges(

    "cache",

    cache_router,

    {

        "cached": END,

        "continue": "query_router",

    }

)





# ============================================================
# QUERY ROUTING
# ============================================================


builder.add_conditional_edges(

    "query_router",

    route_query,

    {

        "rag": "understand",

        "tool": "tool_handler",

        "chat": "chat_handler",

    }

)





# ============================================================
# RAG PIPELINE
# ============================================================


builder.add_edge(
    "understand",
    "normalise_entities"
)


builder.add_edge(
    "normalise_entities",
    "retrieval_planning"
)


builder.add_edge(
    "retrieval_planning",
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
    "evidence_check"
)





# ============================================================
# EVIDENCE ROUTING
# ============================================================


builder.add_conditional_edges(

    "evidence_check",

    evidence_router,

    {

        "generate": "generate",

        "safe": "safe_response",

    }

)





# ============================================================
# FINAL RESPONSE
# ============================================================


builder.add_edge(

    "generate",

    "citations"

)


builder.add_edge(

    "citations",

    "save"

)


builder.add_edge(

    "safe_response",

    "save"

)


builder.add_edge(

    "tool_handler",

    "save"

)


builder.add_edge(

    "chat_handler",

    "save"

)





# ============================================================
# END
# ============================================================


builder.add_edge(

    "save",

    END

)





# ============================================================
# COMPILE GRAPH
# ============================================================


graph = builder.compile()