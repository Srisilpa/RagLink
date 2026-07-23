from rag.retrieval.retriever import (
    SemanticRetriever
)

from rag.retrieval.bm25 import (
    BM25Retriever
)


class HybridRetriever:
    """
    Combines:

        Semantic Retrieval
              +
        BM25 Retrieval
              ↓
        Reciprocal Rank Fusion
              ↓
        Hybrid Results
    """

    def __init__(
        self,
        rrf_k: int = 60
    ):

        # ==========================================
        # SEMANTIC RETRIEVER
        # ==========================================

        self.semantic = (
            SemanticRetriever()
        )


        # ==========================================
        # BM25 RETRIEVER
        # ==========================================

        self.bm25 = (
            BM25Retriever()
        )


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
        top_k: int = 10
    ):

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )


        # ==========================================
        # SEMANTIC SEARCH
        # ==========================================

        semantic_results = (

            self.semantic.retrieve(

                query=query,

                fetch_k=top_k

            )

        )


        # ==========================================
        # BM25 SEARCH
        # ==========================================

        bm25_results = (

            self.bm25.retrieve(

                query=query,

                top_k=top_k

            )

        )


        # ==========================================
        # RRF FUSION
        # ==========================================

        return self.fuse(

            semantic_results,

            bm25_results,

            top_k=top_k

        )


    # ==============================================
    # RRF FUSION
    # ==============================================

    def fuse(
        self,
        semantic_results,
        bm25_results,
        top_k=10
    ):

        scores = {}

        documents = {}


        # ==========================================
        # SEMANTIC RESULTS
        # ==========================================

        for rank, (
            doc,
            score
        ) in enumerate(

            semantic_results,

            start=1

        ):

            key = (
                doc.page_content.strip()
            )


            documents[key] = doc


            scores[key] = (

                scores.get(
                    key,
                    0
                )

                +

                1
                /
                (
                    self.rrf_k
                    +
                    rank
                )

            )


        # ==========================================
        # BM25 RESULTS
        # ==========================================

        for rank, (
            doc,
            score
        ) in enumerate(

            bm25_results,

            start=1

        ):

            key = (
                doc.page_content.strip()
            )


            documents[key] = doc


            scores[key] = (

                scores.get(
                    key,
                    0
                )

                +

                1
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

            key=lambda x: x[1],

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