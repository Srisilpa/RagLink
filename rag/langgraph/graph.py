from langgraph.graph import StateGraph

from rag.langgraph.state import GraphState

from rag.langgraph.nodes import (
    check_cache,
    understand_query,
    retrieve_documents,
    rerank_documents,
    build_context,
    generate_answer,
    save_cache,
)


# ==========================================
# CREATE GRAPH
# ==========================================

builder = StateGraph(
    GraphState
)


# ==========================================
# ADD NODES
# ==========================================

builder.add_node(
    "cache",
    check_cache
)

builder.add_node(
    "understand",
    understand_query
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


# ==========================================
# ENTRY POINT
# ==========================================

builder.set_entry_point(
    "cache"
)


# ==========================================
# GRAPH FLOW
# ==========================================

builder.add_edge(
    "cache",
    "understand"
)

builder.add_edge(
    "understand",
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


# ==========================================
# FINISH
# ==========================================

builder.set_finish_point(
    "save"
)


# ==========================================
# COMPILE
# ==========================================

graph = builder.compile()