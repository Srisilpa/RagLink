from langgraph.graph import StateGraph

from rag.langgraph.state import GraphState
from rag.langgraph.nodes import (
    check_cache,
    retrieve_documents,
    rerank_documents,
    build_context,
    generate_answer,
    save_cache,
)

builder = StateGraph(GraphState)

builder.add_node("cache", check_cache)
builder.add_node("retrieve", retrieve_documents)
builder.add_node("rerank", rerank_documents)
builder.add_node("context", build_context)
builder.add_node("generate", generate_answer)
builder.add_node("save", save_cache)

builder.set_entry_point("cache")

builder.add_edge("cache", "retrieve")
builder.add_edge("retrieve", "rerank")
builder.add_edge("rerank", "context")
builder.add_edge("context", "generate")
builder.add_edge("generate", "save")

builder.set_finish_point("save")

graph = builder.compile()