import os
import pickle

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    BM25 keyword-based retriever.

    Supports metadata filtering.

    Example:

        retriever.retrieve(
            query="Project Meridian database",
            top_k=20,
            filters={
                "document_type": "project"
            }
        )

    Multiple values are also supported:

        filters={
            "document_type": [
                "project",
                "company"
            ]
        }
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

            self.documents = pickle.load(f)

        if not self.documents:

            raise ValueError(
                "No documents found for BM25 retrieval."
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

    # ==============================================
    # TOKENIZATION
    # ==============================================

    @staticmethod
    def _tokenize(
        text: str
    ):

        if not text:

            return []

        return (

            text.lower()
            .split()

        )

    # ==============================================
    # METADATA FILTER
    # ==============================================

    def _matches_filters(
        self,
        document,
        filters: dict
    ):
        """
        Check whether a document matches
        all requested metadata filters.

        Supports:

            filters={
                "document_type": "project"
            }

        and:

            filters={
                "document_type": [
                    "project",
                    "company"
                ]
            }
        """

        # ==========================================
        # NO FILTERS
        # ==========================================

        if not filters:

            return True

        metadata = (
            document.metadata
            or {}
        )

        # ==========================================
        # CHECK ALL FILTERS
        # ==========================================

        for key, expected_value in filters.items():

            actual_value = metadata.get(
                key
            )

            # ======================================
            # MULTIPLE ALLOWED VALUES
            # ======================================

            if isinstance(
                expected_value,
                list
            ):

                if actual_value not in expected_value:

                    return False

            # ======================================
            # SINGLE VALUE
            # ======================================

            else:

                if actual_value != expected_value:

                    return False

        # ==========================================
        # ALL FILTERS MATCHED
        # ==========================================

        return True

    # ==============================================
    # RETRIEVE
    # ==============================================

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: dict = None
    ):
        """
        Retrieve documents using BM25.

        Returns:

            List of (Document, score)
        """

        # ==========================================
        # EMPTY QUERY
        # ==========================================

        if not query or not query.strip():

            return []

        # ==========================================
        # VALIDATE TOP_K
        # ==========================================

        if top_k <= 0:

            raise ValueError(
                "top_k must be greater than 0."
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

            key=lambda i:
                scores[i],

            reverse=True

        )

        # ==========================================
        # BUILD RESULTS
        # ==========================================

        results = []

        for index in ranked_indices:

            document = (
                self.documents[index]
            )

            # ======================================
            # APPLY METADATA FILTER
            # ======================================

            if not self._matches_filters(
                document,
                filters
            ):

                continue

            score = scores[index]

            results.append(

                (
                    document,
                    float(score)
                )

            )

            # ======================================
            # STOP AFTER TOP K
            # ======================================

            if len(results) >= top_k:

                break

        return results

    # ==============================================
    # SEARCH ALIAS
    # ==============================================

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: dict = None
    ):

        return self.retrieve(

            query=query,

            top_k=top_k,

            filters=filters

        )