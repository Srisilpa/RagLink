from rag.retrieval.retriever import (
    SemanticRetriever
)

from rag.retrieval.bm25 import (
    BM25Retriever
)


class HybridRetriever:
    """
    Hybrid retrieval system combining:

        Semantic Retrieval
                +
        BM25 Keyword Retrieval
                ↓
        Reciprocal Rank Fusion (RRF)
                ↓
        Hybrid Candidate Pool
                ↓
        Reranking

    Retrieval flow:

        Semantic Retrieval  -> 20
        BM25 Retrieval      -> 20
                  ↓
             RRF Fusion
                  ↓
        20 Hybrid Candidates
                  ↓
             Reranker
                  ↓
             Top 5 Results
    """

    def __init__(
        self,
        rrf_k: int = 60
    ):

        # ==========================================
        # SEMANTIC RETRIEVER
        # ==========================================

        self.semantic = SemanticRetriever()

        # ==========================================
        # BM25 RETRIEVER
        # ==========================================

        self.bm25 = BM25Retriever()

        # ==========================================
        # RRF CONSTANT
        # ==========================================

        self.rrf_k = rrf_k

    # ==============================================
    # SEARCH
    # ==============================================

    def search(
        self,
        query: str,
        top_k: int = 20,
        filters: dict = None
    ):
        """
        Perform hybrid retrieval.

        top_k represents the number of hybrid
        candidates returned to the reranker.

        Semantic and BM25 each retrieve at least
        20 candidates.

        Example:

            hybrid.search(
                query="Project Meridian database",
                top_k=20,
                filters={
                    "document_type": "project"
                }
            )

        Returns:

            [
                (Document, rrf_score),
                ...
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
        # RETRIEVAL CANDIDATE POOL
        # ==========================================

        # Always retrieve at least 20 documents
        # from each retrieval method.

        candidate_k = max(
            top_k,
            20
        )

        # ==========================================
        # SEMANTIC RETRIEVAL
        # ==========================================

        semantic_results = (

            self.semantic.retrieve(

                query=query,

                return_k=candidate_k,

                fetch_k=candidate_k,

                filters=filters

            )

        )

        print(
            f"Semantic Results: "
            f"{len(semantic_results)}"
        )

        # ==========================================
        # BM25 RETRIEVAL
        # ==========================================

        bm25_results = (

            self.bm25.retrieve(

                query=query,

                top_k=candidate_k,

                filters=filters

            )

        )

        print(
            f"BM25 Results: "
            f"{len(bm25_results)}"
        )

        # ==========================================
        # RRF FUSION
        # ==========================================

        fused_results = self.fuse(

            semantic_results,

            bm25_results,

            top_k=candidate_k

        )

        print(
            f"Hybrid Candidates: "
            f"{len(fused_results)}"
        )

        # ==========================================
        # RETURN HYBRID CANDIDATES
        # ==========================================

        return fused_results

    # ==============================================
    # RRF FUSION
    # ==============================================

    def fuse(
        self,
        semantic_results,
        bm25_results,
        top_k=20
    ):
        """
        Combine semantic and BM25 results using
        Reciprocal Rank Fusion.

        Returns up to top_k hybrid candidates.
        """

        scores = {}

        documents = {}

        # ==========================================
        # PROCESS SEMANTIC RESULTS
        # ==========================================

        for rank, (
            doc,
            retrieval_score
        ) in enumerate(

            semantic_results,

            start=1

        ):

            key = self._document_key(
                doc
            )

            # --------------------------------------
            # STORE DOCUMENT
            # --------------------------------------

            documents[key] = doc

            # --------------------------------------
            # CALCULATE RRF SCORE
            # --------------------------------------

            scores[key] = (

                scores.get(
                    key,
                    0.0
                )

                +

                1.0
                /
                (
                    self.rrf_k
                    +
                    rank
                )

            )

        # ==========================================
        # PROCESS BM25 RESULTS
        # ==========================================

        for rank, (
            doc,
            retrieval_score
        ) in enumerate(

            bm25_results,

            start=1

        ):

            key = self._document_key(
                doc
            )

            # --------------------------------------
            # STORE DOCUMENT
            # --------------------------------------

            documents[key] = doc

            # --------------------------------------
            # CALCULATE RRF SCORE
            # ======================================

            scores[key] = (

                scores.get(
                    key,
                    0.0
                )

                +

                1.0
                /
                (
                    self.rrf_k
                    +
                    rank
                )

            )

        # ==========================================
        # SORT BY RRF SCORE
        # ==========================================

        ranked = sorted(

            scores.items(),

            key=lambda item:
                item[1],

            reverse=True

        )

        # ==========================================
        # RETURN HYBRID CANDIDATES
        # ==========================================

        return [

            (
                documents[key],

                score

            )

            for key, score

            in ranked[
                :top_k
            ]

        ]

    # ==============================================
    # DOCUMENT IDENTITY
    # ==============================================

    @staticmethod
    def _document_key(
        doc
    ):
        """
        Generate a stable identity for a document.

        Content is used as the primary identity
        to prevent duplicate chunks.
        """

        return (
            doc.page_content
            .strip()
        )