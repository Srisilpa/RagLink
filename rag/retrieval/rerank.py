from typing import List, Tuple

from langchain_core.documents import Document

from sentence_transformers import CrossEncoder


class Reranker:
    """
    Cross-encoder document reranker.

    Takes hybrid retrieval results and reorders
    them according to query-document relevance.

    Returns:

        [
            (Document, relevance_score),
            ...
        ]
    """

    def __init__(
        self,
        model_name: str = (
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
    ):

        self.model_name = (
            model_name
        )

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
        top_k: int = 10
    ) -> List[Tuple[Document, float]]:

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

        if not documents:

            return []

        # ==========================================
        # VALIDATE TOP K
        # ==========================================

        if top_k <= 0:

            raise ValueError(
                "top_k must be greater than 0."
            )

        # ==========================================
        # REMOVE DUPLICATES
        # ==========================================

        valid_documents = []

        seen = set()

        for item in documents:

            # --------------------------------------
            # Support both:
            #
            # Document
            #
            # and:
            #
            # (Document, score)
            # --------------------------------------

            if isinstance(
                item,
                tuple
            ):

                document = item[0]

            else:

                document = item

            # --------------------------------------
            # Validate document
            # --------------------------------------

            if not isinstance(
                document,
                Document
            ):

                continue

            if not document.page_content:

                continue

            content = (
                document.page_content
                .strip()
            )

            if not content:

                continue

            # --------------------------------------
            # Deduplicate
            # --------------------------------------

            metadata = (
                document.metadata
                or {}
            )

            key = (

                metadata.get(
                    "source",
                    ""
                ),

                metadata.get(
                    "page",
                    ""
                ),

                content

            )

            if key in seen:

                continue

            seen.add(
                key
            )

            valid_documents.append(
                document
            )

        # ==========================================
        # NO VALID DOCUMENTS
        # ==========================================

        if not valid_documents:

            return []

        # ==========================================
        # CREATE QUERY-DOCUMENT PAIRS
        # ==========================================

        pairs = [

            (

                query,

                document.page_content

            )

            for document

            in valid_documents

        ]

        # ==========================================
        # CROSS ENCODER
        # ==========================================

        scores = self.model.predict(

            pairs,

            show_progress_bar=False

        )

        # ==========================================
        # COMBINE SCORES
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
        # SORT DESCENDING
        # ==========================================

        scored_documents.sort(

            key=lambda item: item[1],

            reverse=True

        )

        # ==========================================
        # RETURN TOP K
        # ==========================================

        return scored_documents[
            :top_k
        ]