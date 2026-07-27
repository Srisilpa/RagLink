from rag.retrieval.retriever import (
    SemanticRetriever
)

from rag.retrieval.bm25 import (
    BM25Retriever
)


class HybridRetriever:
    """
    Hybrid Retrieval System

    Pipeline:

        Semantic Retrieval
                +
        BM25 Keyword Retrieval
                ↓
        Reciprocal Rank Fusion (RRF)
                ↓
        Candidate Pool
                ↓
        Cross-Encoder Reranking

    Supports metadata filtering.
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

        Example:

            filters={
                "document_type": "project"
            }

        Or:

            filters={
                "document_type": [
                    "project",
                    "company"
                ]
            }
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
        # NORMALIZE FILTERS
        # ==========================================

        filters = self._normalize_filters(
            filters
        )

        # ==========================================
        # CANDIDATE POOL SIZE
        # ==========================================

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

            top_k=top_k

        )

        print(
            f"Hybrid Candidates: "
            f"{len(fused_results)}"
        )

        return fused_results

    # ==============================================
    # NORMALIZE FILTERS
    # ==============================================

    @staticmethod
    def _normalize_filters(
        filters
    ):
        """
        Normalize filter values.

        Example:

            {
                "document_type": "project"
            }

        becomes:

            {
                "document_type": "project"
            }

        Lists remain lists.
        """

        if not filters:

            return {}

        normalized = {}

        for key, value in filters.items():

            normalized[key] = value

        return normalized

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
        Combine semantic and BM25 results
        using Reciprocal Rank Fusion.

        RRF Score:

            1 / (rrf_k + rank)

        If a document appears in both
        retrievers, its scores are combined.
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

            documents[key] = doc

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

            documents[key] = doc

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
        # RETURN RESULTS
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
        Generate stable document identity.

        Uses:

            source
            page
            chunk_id
            content

        This prevents accidental merging
        of different chunks.
        """

        metadata = (
            doc.metadata
            or {}
        )

        return (

            metadata.get(
                "source",
                ""
            ),

            str(
                metadata.get(
                    "page",
                    ""
                )
            ),

            metadata.get(
                "chunk_id",
                ""
            ),

            doc.page_content.strip()

        )