from typing import List, Tuple

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder


class Reranker:
    """
    Cross-encoder based document reranker.

    Takes retrieved documents and reranks them
    according to their relevance to the query.

    Returns:
        List of (Document, relevance_score) tuples.
    """

    def __init__(
        self,
        model_name: str = (
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
    ):
        """
        Initialize the cross-encoder reranker.

        Args:
            model_name:
                Hugging Face cross-encoder model name.
        """

        self.model_name = model_name

        self.model = CrossEncoder(
            self.model_name
        )

    # ==========================================
    # RERANK
    # ==========================================

    def rerank(
        self,
        query: str,
        documents: list,
        top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents based on query relevance.

        Args:
            query:
                User's search query.

            documents:
                List of LangChain Document objects.

            top_k:
                Number of top documents to return.

        Returns:
            List of:
                (Document, relevance_score)

            sorted from highest score to lowest score.

        Raises:
            ValueError:
                If query is empty.

            ValueError:
                If documents is None.

            ValueError:
                If top_k is invalid.
        """

        # ==========================================
        # VALIDATE QUERY
        # ==========================================

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        # ==========================================
        # VALIDATE DOCUMENTS
        # ==========================================

        if documents is None:

            raise ValueError(
                "Documents cannot be None."
            )

        # ==========================================
        # HANDLE EMPTY DOCUMENT LIST
        # ==========================================

        if not documents:

            return []

        # ==========================================
        # VALIDATE TOP_K
        # ==========================================

        if top_k <= 0:

            raise ValueError(
                "top_k must be greater than 0."
            )

        # ==========================================
        # VALIDATE DOCUMENT OBJECTS
        # ==========================================

        valid_documents = []

        for document in documents:

            if not isinstance(
                document,
                Document
            ):

                continue

            if not document.page_content:

                continue

            valid_documents.append(
                document
            )

        # ==========================================
        # HANDLE NO VALID DOCUMENTS
        # ==========================================

        if not valid_documents:

            return []

        # ==========================================
        # PREPARE QUERY-DOCUMENT PAIRS
        # ==========================================

        pairs = [

            (
                query,
                document.page_content
            )

            for document in valid_documents

        ]

        # ==========================================
        # CALCULATE RELEVANCE SCORES
        # ==========================================

        scores = self.model.predict(
            pairs
        )

        # ==========================================
        # COMBINE DOCUMENTS AND SCORES
        # ==========================================

        scored_documents = [

            (
                document,
                float(score)
            )

            for document, score
            in zip(
                valid_documents,
                scores
            )

        ]

        # ==========================================
        # SORT BY RELEVANCE SCORE
        # ==========================================

        scored_documents.sort(

            key=lambda item: item[1],

            reverse=True

        )

        # ==========================================
        # RETURN TOP-K DOCUMENTS
        # ==========================================

        return scored_documents[
            :top_k
        ]