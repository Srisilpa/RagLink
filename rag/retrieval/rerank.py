from typing import List, Tuple

from langchain_core.documents import Document

from sentence_transformers import CrossEncoder


class Reranker:
    """
    Cross-encoder document reranker.

    Takes documents returned by the hybrid retriever
    and reorders them based on query-document relevance.

    Input can be:

        Document

    or:

        (Document, retrieval_score)

    Output:

        [
            (Document, rerank_score),
            ...
        ]

    The rerank_score is produced by the CrossEncoder.
    """

    def __init__(
        self,
        model_name: str = (
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
    ):

        # ==========================================
        # MODEL NAME
        # ==========================================

        self.model_name = model_name

        # ==========================================
        # LOAD CROSS ENCODER
        # ==========================================

        self.model = CrossEncoder(
            self.model_name
        )

    # ==========================================
    # RERANK DOCUMENTS
    # ==========================================

    def rerank(
        self,
        query: str,
        documents: list,
        top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents using a CrossEncoder.

        Parameters
        ----------
        query : str
            User query or rewritten query.

        documents : list
            List containing either:

                Document

            or:

                (Document, retrieval_score)

        top_k : int
            Number of documents to return
            after reranking.

        Returns
        -------
        List[Tuple[Document, float]]

            Example:

            [
                (document1, 8.52),
                (document2, 7.91),
                (document3, 6.84)
            ]
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
        # EMPTY DOCUMENT LIST
        # ==========================================

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
        # EXTRACT AND VALIDATE DOCUMENTS
        # ==========================================

        valid_documents = []

        seen = set()

        for item in documents:

            # --------------------------------------
            # SUPPORT BOTH FORMATS
            #
            # 1. Document
            #
            # 2. (Document, score)
            # --------------------------------------

            if isinstance(
                item,
                tuple
            ):

                document = item[0]

                # Original retrieval score
                # from Hybrid Retriever
                retrieval_score = (
                    item[1]
                    if len(item) > 1
                    else None
                )

            else:

                document = item

                retrieval_score = None

            # --------------------------------------
            # CHECK DOCUMENT TYPE
            # --------------------------------------

            if not isinstance(
                document,
                Document
            ):

                continue

            # --------------------------------------
            # CHECK PAGE CONTENT
            # --------------------------------------

            if not document.page_content:

                continue

            content = (
                document.page_content
                .strip()
            )

            if not content:

                continue

            # --------------------------------------
            # GET METADATA
            # --------------------------------------

            metadata = (
                document.metadata
                or {}
            )

            # --------------------------------------
            # DOCUMENT IDENTITY
            #
            # Used to remove duplicate chunks.
            # --------------------------------------

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

            # --------------------------------------
            # SKIP DUPLICATES
            # --------------------------------------

            if key in seen:

                continue

            seen.add(
                key
            )

            # --------------------------------------
            # STORE ORIGINAL RETRIEVAL SCORE
            #
            # For example:
            #
            # RRF score
            #
            # This is useful for debugging
            # and observability.
            # --------------------------------------

            if retrieval_score is not None:

                document.metadata[
                    "retrieval_score"
                ] = float(
                    retrieval_score
                )

            # --------------------------------------
            # ADD VALID DOCUMENT
            # --------------------------------------

            valid_documents.append(
                document
            )

        # ==========================================
        # CHECK IF VALID DOCUMENTS EXIST
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
        # CROSS ENCODER PREDICTION
        # ==========================================

        scores = self.model.predict(

            pairs,

            show_progress_bar=False

        )

        # ==========================================
        # CREATE SCORED DOCUMENT LIST
        # ==========================================

        scored_documents = []

        for document, score in zip(

            valid_documents,

            scores

        ):

            # --------------------------------------
            # CONVERT SCORE TO FLOAT
            # --------------------------------------

            score = float(
                score
            )

            # --------------------------------------
            # STORE RERANK SCORE IN METADATA
            # --------------------------------------

            document.metadata[
                "rerank_score"
            ] = score

            # --------------------------------------
            # ADD DOCUMENT + SCORE
            # --------------------------------------

            scored_documents.append(

                (
                    document,
                    score
                )

            )

        # ==========================================
        # SORT BY RERANK SCORE
        #
        # Highest relevance first.
        # ==========================================

        scored_documents.sort(

            key=lambda item: item[1],

            reverse=True

        )

        # ==========================================
        # RETURN TOP K DOCUMENTS
        # ==========================================

        return scored_documents[
            :top_k
        ]