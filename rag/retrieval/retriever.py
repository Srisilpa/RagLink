from rag.embeddings.embedding_model import get_embedding_model
from rag.vectorstore.chroma import load_vectorstore


class Retriever:
    """
    Handles semantic retrieval from the Chroma vector database.
    """

    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.vectorstore = load_vectorstore(self.embedding_model)

    def retrieve(self, query: str, return_k: int = 5, fetch_k: int = 10):
        """
        Retrieve the top unique documents for a given query.

        Args:
            query (str): User query.
            return_k (int): Number of unique documents to return.
            fetch_k (int): Number of documents to fetch initially.

        Returns:
            list: List of tuples (Document, score).
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        # Fetch more documents than required
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=fetch_k
        )

        # Remove duplicate chunks
        unique_results = []
        seen = set()

        for doc, score in results:
            content = doc.page_content.strip()

            if content not in seen:
                seen.add(content)
                unique_results.append((doc, score))

            if len(unique_results) >= return_k:
                break

        return unique_results