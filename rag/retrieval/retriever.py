import os

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
        # BUILD CHROMA FILTER
        # ==========================================

        chroma_filter = (
            self._build_chroma_filter(
                filters
            )
        )

        # ==========================================
        # SEMANTIC SEARCH
        # ==========================================

        if chroma_filter:

            results = (

                self.vectorstore
                .similarity_search_with_score(

                    query=query,

                    k=fetch_k,

                    filter=chroma_filter

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
        # RETURN
        # ==========================================

        return results[
            :return_k
        ]

    # ==========================================
    # BUILD CHROMA FILTER
    # ==========================================

    @staticmethod
    def _build_chroma_filter(
        filters
    ):

        if not filters:

            return None

        conditions = []

        for key, value in filters.items():

            # --------------------------------------
            # MULTIPLE VALUES
            # --------------------------------------

            if isinstance(
                value,
                list
            ):

                if len(value) == 1:

                    conditions.append(

                        {
                            key:
                                value[0]
                        }

                    )

                elif len(value) > 1:

                    conditions.append(

                        {
                            "$or": [

                                {
                                    key:
                                        item
                                }

                                for item in value

                            ]
                        }

                    )

            # --------------------------------------
            # SINGLE VALUE
            # --------------------------------------

            else:

                conditions.append(

                    {
                        key:
                            value
                    }

                )

        # ==========================================
        # SINGLE CONDITION
        # ==========================================

        if len(conditions) == 1:

            return conditions[0]

        # ==========================================
        # MULTIPLE CONDITIONS
        # ==========================================

        if len(conditions) > 1:

            return {

                "$and":
                    conditions

            }

        return None


# ==============================================
# BACKWARD COMPATIBILITY
# ==============================================

SemanticRetriever = Retriever