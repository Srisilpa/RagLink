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
        Top-K Hybrid Results
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
        top_k: int = 15
    ):
        """
        Perform hybrid retrieval.

        Semantic retrieval and BM25 retrieval each
        retrieve a larger candidate pool.

        Results are combined using Reciprocal Rank Fusion.

        Returns:
            List of (Document, RRF score)
        """

        # ==========================================
        # VALIDATE QUERY
        # ==========================================

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        # ==========================================
        # VALIDATE TOP_K
        # ==========================================

        if top_k <= 0:

            raise ValueError(
                "top_k must be greater than 0."
            )

        # ==========================================
        # CANDIDATE POOL
        # ==========================================

        # Retrieve more documents from both systems
        # before applying RRF fusion.

        candidate_k = max(
            top_k,
            20
        )

        # ==========================================
        # SEMANTIC SEARCH
        # ==========================================

        semantic_results = (

            self.semantic.retrieve(

                query=query,

                return_k=candidate_k,

                fetch_k=candidate_k

            )

        )

        print(
            f"Semantic Results: "
            f"{len(semantic_results)}"
        )

        # ==========================================
        # BM25 SEARCH
        # ==========================================

        bm25_results = (

            self.bm25.retrieve(

                query=query,

                top_k=candidate_k

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

            top_k=top_k

        )

        return fused_results

    # ==============================================
    # RRF FUSION
    # ==============================================

    def fuse(
        self,
        semantic_results,
        bm25_results,
        top_k=15
    ):
        """
        Combine semantic and BM25 results using
        Reciprocal Rank Fusion.
        """

        scores = {}

        documents = {}

        # ==========================================
        # PROCESS SEMANTIC RESULTS
        # ==========================================

        for rank, (
            doc,
            score
        ) in enumerate(

            semantic_results,

            start=1

        ):

            # --------------------------------------
            # Use content as document identity
            # --------------------------------------

            key = (
                doc.page_content
                .strip()
            )

            # --------------------------------------
            # Store document
            # --------------------------------------

            documents[key] = doc

            # --------------------------------------
            # RRF score
            # --------------------------------------

            scores[key] = (

                scores.get(
                    key,
                    0
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
            score
        ) in enumerate(

            bm25_results,

            start=1

        ):

            # --------------------------------------
            # Use content as document identity
            # --------------------------------------

            key = (
                doc.page_content
                .strip()
            )

            # --------------------------------------
            # Store document
            # --------------------------------------

            documents[key] = doc

            # --------------------------------------
            # RRF score
            # --------------------------------------

            scores[key] = (

                scores.get(
                    key,
                    0
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
        # RETURN TOP RESULTS
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