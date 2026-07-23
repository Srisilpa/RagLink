from rag.embeddings.embedding_model import (
    get_embedding_model
)

from rag.vectorstore.chroma import (
    load_vectorstore
)


class SemanticRetriever:
    """
    Handles semantic retrieval from ChromaDB.
    """

    def __init__(self):

        self.embedding_model = (
            get_embedding_model()
        )

        self.vectorstore = (
            load_vectorstore(
                self.embedding_model
            )
        )


    def retrieve(
        self,
        query: str,
        fetch_k: int = 10
    ):

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )


        results = (

            self.vectorstore
            .similarity_search_with_score(

                query=query,

                k=fetch_k

            )

        )


        return results