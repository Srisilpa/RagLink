from langgraph.graph import StateGraph

from rag.langgraph.state import GraphState

from rag.langgraph.nodes import (
    check_cache,
    understand_query,
    normalise_entities_node,
    retrieval_planning_node,
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

# ------------------------------------------
# CACHE
# ------------------------------------------

builder.add_node(
    "cache",
    check_cache
)


# ------------------------------------------
# QUERY UNDERSTANDING
# ------------------------------------------

builder.add_node(
    "understand",
    understand_query
)


# ------------------------------------------
# ENTITY NORMALISATION
# ------------------------------------------

builder.add_node(
    "normalise_entities",
    normalise_entities_node
)


# ------------------------------------------
# RETRIEVAL PLANNING
# ------------------------------------------

builder.add_node(
    "retrieval_planning",
    retrieval_planning_node
)


# ------------------------------------------
# RETRIEVAL
# ------------------------------------------

builder.add_node(
    "retrieve",
    retrieve_documents
)


# ------------------------------------------
# RERANKING
# ------------------------------------------

builder.add_node(
    "rerank",
    rerank_documents
)


# ------------------------------------------
# CONTEXT REFINEMENT
# ------------------------------------------

builder.add_node(
    "context",
    build_context
)


# ------------------------------------------
# ANSWER GENERATION
# ------------------------------------------

builder.add_node(
    "generate",
    generate_answer
)


# ------------------------------------------
# CACHE SAVE
# ------------------------------------------

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

# ------------------------------------------
# CACHE
# ------------------------------------------

builder.add_edge(
    "cache",
    "understand"
)


# ------------------------------------------
# QUERY UNDERSTANDING
# ------------------------------------------

builder.add_edge(
    "understand",
    "normalise_entities"
)


# ------------------------------------------
# ENTITY NORMALISATION
# ------------------------------------------

builder.add_edge(
    "normalise_entities",
    "retrieval_planning"
)


# ------------------------------------------
# RETRIEVAL PLANNING
# ------------------------------------------

builder.add_edge(
    "retrieval_planning",
    "retrieve"
)


# ------------------------------------------
# HYBRID RETRIEVAL
# ------------------------------------------

builder.add_edge(
    "retrieve",
    "rerank"
)


# ------------------------------------------
# CROSS-ENCODER RERANKING
# ------------------------------------------

builder.add_edge(
    "rerank",
    "context"
)


# ------------------------------------------
# CONTEXT REFINEMENT
# ------------------------------------------

builder.add_edge(
    "context",
    "generate"
)


# ------------------------------------------
# LLM GENERATION
# ------------------------------------------

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
# COMPILE GRAPH
# ==========================================

graph = builder.compile()