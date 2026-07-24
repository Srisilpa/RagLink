from rag.cache.memory_cache import MemoryCache
from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.rerank import Reranker
from rag.generation.prompt import build_prompt
from rag.generation.llm import GroqLLM


cache = MemoryCache()
retriever = HybridRetriever()
reranker = Reranker()
llm = GroqLLM()


def check_cache(state):

    question = state["question"]

    cached = cache.get(question)

    if cached:

        state["answer"] = cached
        state["cache_hit"] = True

    else:

        state["cache_hit"] = False

    return state


def retrieve_documents(state):

    if state["cache_hit"]:
        return state

    docs = retriever.search(
        question=state["question"]
    )

    state["retrieved_docs"] = [
        doc
        for doc, _ in docs
    ]

    return state


def rerank_documents(state):

    if state["cache_hit"]:
        return state

    docs = reranker.rerank(
        state["question"],
        state["retrieved_docs"]
    )

    state["reranked_docs"] = docs

    return state


def build_context(state):

    if state["cache_hit"]:
        return state

    context = ""

    for doc in state["reranked_docs"]:

        context += doc.page_content
        context += "\n\n"

    state["context"] = context

    return state


def generate_answer(state):

    if state["cache_hit"]:
        return state

    prompt = build_prompt(
        question=state["question"],
        context=state["context"]
    )

    answer = llm.generate(
        prompt
    )

    state["answer"] = answer

    return state


def save_cache(state):

    if not state["cache_hit"]:

        cache.set(
            state["question"],
            state["answer"]
        )

    return state