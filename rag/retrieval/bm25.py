import os
import pickle

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    BM25 keyword-based retriever.

    Supports optional metadata filtering.

    Example:

        retriever.retrieve(
            query="Project Meridian database",
            top_k=20,
            filters={
                "document_type": "project"
            }
        )
    """

    def __init__(
        self,
        chunks_path: str = "data/chunks.pkl"
    ):

        self.chunks_path = chunks_path

        # ==========================================
        # CHECK FILE
        # ==========================================

        if not os.path.exists(
            self.chunks_path
        ):

            raise FileNotFoundError(

                f"BM25 chunks file not found: "
                f"{self.chunks_path}"

            )

        # ==========================================
        # LOAD DOCUMENTS
        # ==========================================

        with open(
            self.chunks_path,
            "rb"
        ) as f:

            self.documents = pickle.load(
                f
            )

        if not self.documents:

            raise ValueError(

                "No documents found for "
                "BM25 retrieval."

            )

        # ==========================================
        # TOKENIZE DOCUMENTS
        # ==========================================

        self.tokenized_documents = [

            self._tokenize(
                doc.page_content
            )

            for doc in self.documents

        ]

        # ==========================================
        # CREATE BM25 INDEX
        # ==========================================

        self.bm25 = BM25Okapi(

            self.tokenized_documents

        )

    # ==========================================
    # TOKENIZATION
    # ==========================================

    def _tokenize(
        self,
        text: str
    ):

        if not text:

            return []

        return (

            text.lower()
            .split()

        )

    # ==========================================
    # METADATA FILTER
    # ==========================================

    def _matches_filters(
        self,
        document,
        filters: dict
    ):
        """
        Check whether a document matches
        all requested metadata filters.

        Example:

            filters = {
                "document_type": "project"
            }

        Returns:

            True
            or
            False
        """

        # No filters means every document matches

        if not filters:

            return True

        metadata = (
            document.metadata
            or {}
        )

        # ==========================================
        # CHECK EACH FILTER
        # ==========================================

        for key, expected_value in filters.items():

            actual_value = metadata.get(
                key
            )

            # --------------------------------------
            # FILTER DOES NOT MATCH
            # --------------------------------------

            if actual_value != expected_value:

                return False

        # ==========================================
        # ALL FILTERS MATCHED
        # ==========================================

        return True

    # ==========================================
    # RETRIEVE
    # ==========================================

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: dict = None
    ):
        """
        Retrieve documents using BM25.

        Optional metadata filters are applied
        before ranking results.
        """

        # ==========================================
        # HANDLE EMPTY QUERY
        # ==========================================

        if not query or not query.strip():

            return []

        # ==========================================
        # VALIDATE TOP K
        # ==========================================

        if top_k <= 0:

            raise ValueError(

                "top_k must be greater than 0."

            )

        # ==========================================
        # VALIDATE FILTERS
        # ==========================================

        if filters is not None:

            if not isinstance(
                filters,
                dict
            ):

                raise ValueError(

                    "filters must be a dictionary."

                )

        # ==========================================
        # TOKENIZE QUERY
        # ==========================================

        query_tokens = self._tokenize(
            query
        )

        # ==========================================
        # GET BM25 SCORES
        # ==========================================

        scores = self.bm25.get_scores(
            query_tokens
        )

        # ==========================================
        # RANK DOCUMENTS
        # ==========================================

        ranked_indices = sorted(

            range(
                len(scores)
            ),

            key=lambda i: scores[i],

            reverse=True

        )

        # ==========================================
        # BUILD RESULTS
        # ==========================================

        results = []

        for index in ranked_indices:

            # --------------------------------------
            # GET DOCUMENT
            # --------------------------------------

            document = (
                self.documents[index]
            )

            # --------------------------------------
            # APPLY METADATA FILTER
            # --------------------------------------

            if not self._matches_filters(

                document,

                filters

            ):

                continue

            # --------------------------------------
            # GET SCORE
            # --------------------------------------

            score = scores[index]

            # --------------------------------------
            # ADD RESULT
            # --------------------------------------

            results.append(

                (

                    document,

                    float(score)

                )

            )

            # --------------------------------------
            # STOP AFTER TOP K
            # --------------------------------------

            if len(results) >= top_k:

                break

        return results

    # ==========================================
    # SEARCH
    # ==========================================

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: dict = None
    ):
        """
        Backward-compatible search method.
        """

        return self.retrieve(

            query=query,

            top_k=top_k,

            filters=filters

        )