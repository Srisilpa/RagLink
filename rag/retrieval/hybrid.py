from rag.retrieval.retriever import Retriever
from rag.retrieval.bm25 import BM25Retriever


class HybridRetriever:

    def __init__(self):

        self.semantic = Retriever()
        self.bm25 = BM25Retriever()

    def search(
        self,
        query: str,
        semantic_k: int = 3,
        bm25_k: int = 3
    ):

        semantic_results = self.semantic.retrieve(
            query=query,
            return_k=semantic_k,
            fetch_k=10
        )

        bm25_results = self.bm25.search(
            query=query,
            k=bm25_k
        )

        merged = []
        seen = set()

        # Semantic results first
        for doc, score in semantic_results:

            text = doc.page_content.strip()

            if text not in seen:
                seen.add(text)
                merged.append((doc, score))

        # Then BM25 results
        for doc, score in bm25_results:

            text = doc.page_content.strip()

            if text not in seen:
                seen.add(text)
                merged.append((doc, score))

        return merged