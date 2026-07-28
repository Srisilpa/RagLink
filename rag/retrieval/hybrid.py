from langchain_core.documents import Document

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

    Supports:

        1. No metadata filtering

            filters={}

        2. Single-domain filtering

            filters={
                "document_type": "project"
            }

        3. Multi-domain filtering

            filters={
                "document_type": [
                    "project",
                    "infrastructure"
                ]
            }

    Important:

        The semantic and BM25 retrievers are responsible
        for applying the actual metadata filtering.

        This class only normalises the filter structure
        and passes it to both retrieval systems.
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
# RELOAD BM25 INDEX
# ==============================================

    def reload_bm25(self):

        print(
        "\nReloading BM25 index..."
        )

        self.bm25 = BM25Retriever()

        print(
        "BM25 index reloaded successfully."
        )

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

        Examples:

        ------------------------------------------------
        No filter
        ------------------------------------------------

            filters={}

        This searches across all indexed documents.

        ------------------------------------------------
        Single domain
        ------------------------------------------------

            filters={
                "document_type": "project"
            }

        ------------------------------------------------
        Multiple domains
        ------------------------------------------------

            filters={
                "document_type": [
                    "project",
                    "infrastructure"
                ]
            }

        The multi-domain filter is passed to both
        semantic and BM25 retrieval.
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
        # DEBUG FILTERS
        # ==========================================

        print(
            "\n"
            + "=" * 60
        )

        print(
            "HYBRID RETRIEVAL"
        )

        print(
            "=" * 60
        )

        print(
            f"Query: {query}"
        )

        print(
            f"Filters: {filters}"
        )

        print(
            "=" * 60
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
        Normalize metadata filters.

        Supported:

            {}

        or:

            {
                "document_type": "project"
            }

        or:

            {
                "document_type": [
                    "project",
                    "company"
                ]
            }

        Empty filters mean:

            Do not apply metadata filtering.

        Lists are preserved because the underlying
        retrievers must decide how to translate
        multi-value filters into their respective
        database/search operations.
        """

        # ==========================================
        # NO FILTERS
        # ==========================================

        if not filters:

            return {}

        # ==========================================
        # VALIDATE FILTER TYPE
        # ==========================================

        if not isinstance(
            filters,
            dict
        ):

            raise TypeError(
                "filters must be a dictionary."
            )

        normalized = {}

        # ==========================================
        # PROCESS FILTERS
        # ==========================================

        for key, value in filters.items():

            # --------------------------------------
            # IGNORE EMPTY VALUES
            # --------------------------------------

            if value is None:

                continue

            if value == "":

                continue

            if isinstance(
                value,
                list
            ):

                # Remove empty values

                cleaned_values = [

                    item

                    for item in value

                    if item is not None
                    and item != ""

                ]

                # Empty list means:
                # no restriction

                if not cleaned_values:

                    continue

                normalized[
                    key
                ] = cleaned_values

            else:

                normalized[
                    key
                ] = value

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

            documents[
                key
            ] = doc

            scores[
                key
            ] = (

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

            documents[
                key
            ] = doc

            scores[
                key
            ] = (

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
                documents[
                    key
                ],

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



    