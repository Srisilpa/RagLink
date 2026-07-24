from rag.embeddings.embedding_model import (
    get_embedding_model
)

from rag.vectorstore.chroma import (
    load_vectorstore
)


class Retriever:
    """
    Semantic retriever using ChromaDB.

    Retrieves documents based on semantic similarity
    between the query and indexed document chunks.

    API:

        retriever = Retriever()

        results = retriever.retrieve(
            query="Leave policy",
            return_k=5,
            fetch_k=10
        )

    Returns:

        [(document, score), ...]

    """

    def __init__(self):

        # ==========================================
        # LOAD EMBEDDING MODEL
        # ==========================================

        self.embedding_model = (
            get_embedding_model()
        )

        # ==========================================
        # LOAD VECTOR STORE
        # ==========================================

        self.vectorstore = (
            load_vectorstore(
                self.embedding_model
            )
        )

    # ==========================================
    # RETRIEVE
    # ==========================================

    def retrieve(
        self,
        query: str,
        return_k: int = 10,
        fetch_k: int = 10
    ):
        """
        Retrieve semantically similar documents.

        Args:
            query:
                User's search query.

            return_k:
                Number of documents returned
                to the caller.

            fetch_k:
                Number of documents initially
                fetched from ChromaDB.

        Returns:
            List of:

                [(document, score), ...]

        Raises:
            ValueError:
                If query is empty.

            ValueError:
                If return_k or fetch_k is invalid.
        """

        # ==========================================
        # VALIDATE QUERY
        # ==========================================

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        # ==========================================
        # VALIDATE RETURN_K
        # ==========================================

        if return_k <= 0:

            raise ValueError(
                "return_k must be greater than 0."
            )

        # ==========================================
        # VALIDATE FETCH_K
        # ==========================================

        if fetch_k <= 0:

            raise ValueError(
                "fetch_k must be greater than 0."
            )

        # ==========================================
        # ENSURE FETCH_K >= RETURN_K
        # ==========================================

        if fetch_k < return_k:

            fetch_k = return_k

        # ==========================================
        # SEMANTIC SEARCH
        # ==========================================

        results = (

            self.vectorstore
            .similarity_search_with_score(

                query=query,

                k=fetch_k

            )

        )

        # ==========================================
        # RETURN TOP RESULTS
        # ==========================================

        return results[:return_k]


# ==============================================
# BACKWARD COMPATIBILITY
# ==============================================

SemanticRetriever = Retriever