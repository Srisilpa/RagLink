from rag.embeddings.embedding_model import (
    get_embedding_model
)

from rag.vectorstore.chroma import (
    load_vectorstore
)


class Retriever:
    """
    Semantic Retriever using ChromaDB.

    Retrieves a larger candidate set so that
    the reranker has enough documents to choose from.
    """

    def __init__(self):

        # ==========================================
        # EMBEDDING MODEL
        # ==========================================

        self.embedding_model = (
            get_embedding_model()
        )

        # ==========================================
        # VECTOR STORE
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
        return_k: int = 20,
        fetch_k: int = 20
    ):

        # ==========================================
        # VALIDATE QUERY
        # ==========================================

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        # ==========================================
        # VALIDATE K
        # ==========================================

        if return_k <= 0:

            raise ValueError(
                "return_k must be greater than 0."
            )

        if fetch_k <= 0:

            raise ValueError(
                "fetch_k must be greater than 0."
            )

        # ==========================================
        # ENSURE FETCH >= RETURN
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
        # RETURN
        # ==========================================

        return results[
            :return_k
        ]


# ==============================================
# BACKWARD COMPATIBILITY
# ==============================================

SemanticRetriever = Retriever