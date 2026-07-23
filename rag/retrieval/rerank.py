import os
import pickle

from sklearn.metrics.pairwise import cosine_similarity

from rag.embeddings.embedding_model import (
    get_embedding_model
)


class Reranker:
    """
    Reranks retrieved documents using
    embedding cosine similarity.
    """

    def __init__(
        self,
        chunks_path: str = "data/chunks.pkl",
        embeddings_path: str = "data/chunk_embeddings.pkl"
    ):

        # ==========================================
        # EMBEDDING MODEL
        # ==========================================

        self.embedding_model = (
            get_embedding_model()
        )


        # ==========================================
        # CHECK FILES
        # ==========================================

        if not os.path.exists(
            chunks_path
        ):

            raise FileNotFoundError(
                f"Chunks file not found: "
                f"{chunks_path}"
            )


        if not os.path.exists(
            embeddings_path
        ):

            raise FileNotFoundError(
                f"Chunk embeddings file not found: "
                f"{embeddings_path}"
            )


        # ==========================================
        # LOAD CHUNKS
        # ==========================================

        with open(
            chunks_path,
            "rb"
        ) as f:

            self.all_documents = (
                pickle.load(f)
            )


        # ==========================================
        # LOAD EMBEDDINGS
        # ==========================================

        with open(
            embeddings_path,
            "rb"
        ) as f:

            self.all_embeddings = (
                pickle.load(f)
            )


        # ==========================================
        # CREATE LOOKUP
        # ==========================================

        self.embedding_lookup = {}


        for doc, embedding in zip(

            self.all_documents,

            self.all_embeddings

        ):

            self.embedding_lookup[

                doc.page_content.strip()

            ] = embedding


    # ==============================================
    # RERANK
    # ==============================================

    def rerank(
        self,
        query: str,
        documents,
        top_k: int = 5
    ):

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )


        if not documents:

            return []


        # ==========================================
        # QUERY EMBEDDING
        # ==========================================

        query_embedding = (

            self.embedding_model
            .embed_query(
                query
            )

        )


        ranked = []


        # ==========================================
        # CALCULATE SIMILARITY
        # ==========================================

        for doc in documents:

            content = (
                doc.page_content.strip()
            )


            embedding = (

                self.embedding_lookup
                .get(
                    content
                )

            )


            if embedding is None:

                continue


            similarity = (

                cosine_similarity(

                    [query_embedding],

                    [embedding]

                )[0][0]

            )


            ranked.append(

                (

                    doc,

                    float(
                        similarity
                    )

                )

            )


        # ==========================================
        # SORT
        # ==========================================

        ranked.sort(

            key=lambda x: x[1],

            reverse=True

        )


        # ==========================================
        # RETURN DOCUMENTS ONLY
        # ==========================================

        return [

            doc

            for doc, score

            in ranked[
                :top_k
            ]

        ]