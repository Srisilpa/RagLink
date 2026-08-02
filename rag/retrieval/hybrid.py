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

        Query Plan
             |
             |
        Multiple Queries
             |
             |
    Semantic Retrieval + BM25 Retrieval
             |
             |
        Reciprocal Rank Fusion
             |
             |
        Candidate Pool

    Supports:

        - Semantic search
        - BM25 search
        - Multi query retrieval
        - Multi domain filtering
        - Metadata filtering
    """


    def __init__(
        self,
        rrf_k: int = 60
    ):

        self.semantic = SemanticRetriever()

        self.bm25 = BM25Retriever()

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
        filters: dict = None,
        retrieval_plan: dict = None
    ):
        """
        Hybrid search.

        Supports:

        Normal:

            search(
                query="AWS architecture"
            )


        Planned retrieval:

            retrieval_plan={
                "search_queries":[
                    "Project Meridian",
                    "AWS infrastructure"
                ],

                "metadata_filters":{
                    "document_type":[
                        "project",
                        "infrastructure"
                    ]
                }
            }

        """


        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )



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
        # RETRIEVAL PLAN SUPPORT
        # ==========================================

        search_queries = [
            query
        ]


        if retrieval_plan:


            planned_queries = retrieval_plan.get(
                "search_queries",
                []
            )


            if planned_queries:

                search_queries = list(
                    dict.fromkeys(
                        planned_queries
                    )
                )



            planned_filters = retrieval_plan.get(
                "metadata_filters",
                {}
            )


            if planned_filters:

                filters.update(

                    self._normalize_filters(
                        planned_filters
                    )

                )



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
            f"Queries: {search_queries}"
        )

        print(
            f"Filters: {filters}"
        )

        print(
            "=" * 60
        )



        candidate_k = max(
            top_k,
            20
        )



        # ==========================================
        # SEMANTIC RETRIEVAL
        # ==========================================

        semantic_results = []


        for search_query in search_queries:


            results = self.semantic.retrieve(

                query=search_query,

                return_k=candidate_k,

                fetch_k=candidate_k,

                filters=filters

            )


            semantic_results.extend(
                results
            )



        print(
            f"Semantic Results: "
            f"{len(semantic_results)}"
        )



        # ==========================================
        # BM25 RETRIEVAL
        # ==========================================

        bm25_results = []


        for search_query in search_queries:


            results = self.bm25.retrieve(

                query=search_query,

                top_k=candidate_k,

                filters=filters

            )


            bm25_results.extend(
                results
            )


        print(
            f"BM25 Results: "
            f"{len(bm25_results)}"
        )



        # ==========================================
        # REMOVE DUPLICATES
        # ==========================================

        semantic_results = self._remove_duplicates(
            semantic_results
        )


        bm25_results = self._remove_duplicates(
            bm25_results
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
                    "infrastructure"
                ]
            }

        """

        if not filters:

            return {}



        if not isinstance(
            filters,
            dict
        ):

            raise TypeError(
                "filters must be a dictionary."
            )



        normalized = {}



        for key, value in filters.items():



            # Ignore empty values

            if value is None:

                continue


            if value == "":

                continue



            # Handle list filters

            if isinstance(
                value,
                list
            ):


                cleaned_values = [

                    item

                    for item in value

                    if item is not None
                    and item != ""

                ]



                if cleaned_values:

                    normalized[key] = cleaned_values



            else:


                normalized[key] = value



        return normalized




    # ==============================================
    # REMOVE DUPLICATES
    # ==============================================

    def _remove_duplicates(
        self,
        results
    ):
        """
        Remove duplicate chunks.

        Prevents repeated results when
        multiple expanded queries retrieve
        the same document chunk.
        """


        seen = set()


        cleaned = []



        for item in results:


            doc = item[0]


            key = self._document_key(
                doc
            )


            if key not in seen:


                seen.add(
                    key
                )


                cleaned.append(
                    item
                )



        return cleaned





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
        Reciprocal Rank Fusion.

        Formula:

            score =
            1 / (rrf_k + rank)

        Documents appearing in both
        retrievers get higher ranking.
        """


        scores = {}

        documents = {}



        # ------------------------------------------
        # Semantic Results
        # ------------------------------------------

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

                (
                    1.0
                    /
                    (
                        self.rrf_k
                        +
                        rank
                    )
                )

            )



        # ------------------------------------------
        # BM25 Results
        # ------------------------------------------

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

                (
                    1.0
                    /
                    (
                        self.rrf_k
                        +
                        rank
                    )
                )

            )



        # ------------------------------------------
        # SORT
        # ------------------------------------------

        ranked = sorted(

            scores.items(),

            key=lambda item:
                item[1],

            reverse=True

        )



        return [

            (
                documents[key],

                score

            )

            for key, score

            in ranked[:top_k]

        ]


        # ============================================================
    # MULTI QUERY SEARCH
    # ============================================================

    def search_multiple(
        self,
        queries,
        top_k=5,
        filters=None,
    ):
        """
        Hybrid retrieval for multiple queries.

        Used by LangGraph retrieval node.
        """

        if not queries:

            return []


        all_results = []


        for query in queries:

            results = self.search(

                query=query,

                top_k=top_k,

                filters=filters,

            )

            all_results.extend(
                results
            )


        # Remove duplicate chunks

        unique_results = []

        seen = set()


        for doc, score in all_results:


            key = self._document_key(
                doc
            )


            if key in seen:

                continue


            seen.add(key)


            unique_results.append(
                (
                    doc,
                    score
                )
            )


        return unique_results[:top_k]

    # ==============================================
    # DOCUMENT IDENTITY
    # ==============================================

    @staticmethod
    def _document_key(
        doc
    ):
        """
        Stable chunk identity.
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