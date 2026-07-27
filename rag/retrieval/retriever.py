from rag.embeddings.embedding_model import (
    get_embedding_model
)

from rag.vectorstore.chroma import (
    load_vectorstore
)


class Retriever:
    """
    Semantic Retriever using ChromaDB.

    Supports optional metadata filtering.

    Example:

        retriever.retrieve(
            query="What is Project Meridian?",
            return_k=20,
            filters={
                "document_type": "project"
            }
        )

    The metadata filter is applied directly
    by ChromaDB before returning results.
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
        fetch_k: int = 20,
        filters: dict = None
    ):
        """
        Retrieve semantically relevant documents.

        Parameters
        ----------
        query : str
            Search query.

        return_k : int
            Number of documents returned.

        fetch_k : int
            Number of documents fetched from ChromaDB.

        filters : dict, optional
            Metadata filters.

        Example:

            {
                "document_type": "project"
            }

        Returns
        -------
        List[Tuple[Document, float]]
        """

        # ==========================================
        # VALIDATE QUERY
        # ==========================================

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        # ==========================================
        # VALIDATE RETURN K
        # ==========================================

        if return_k <= 0:

            raise ValueError(
                "return_k must be greater than 0."
            )

        # ==========================================
        # VALIDATE FETCH K
        # ==========================================

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
        # CLEAN FILTERS
        # ==========================================

        if filters is not None:

            if not isinstance(
                filters,
                dict
            ):

                raise ValueError(
                    "filters must be a dictionary."
                )

            # Remove empty filter values
            filters = {

                key: value

                for key, value
                in filters.items()

                if value is not None
                and value != ""

            }

        # ==========================================
        # SEMANTIC SEARCH
        # ==========================================

        if filters:

            results = (

                self.vectorstore
                .similarity_search_with_score(

                    query=query,

                    k=fetch_k,

                    filter=filters

                )

            )

        else:

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

        return results[
            :return_k
        ]


# ==============================================
# BACKWARD COMPATIBILITY
# ==============================================

SemanticRetriever = Retriever