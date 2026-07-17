from typing import TypedDict, List
from langchain_core.documents import Document


class GraphState(TypedDict):

    question: str

    retrieved_docs: List[Document]

    reranked_docs: List[Document]

    context: str

    answer: str

    cache_hit: bool