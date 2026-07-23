import os
import pickle

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    BM25 keyword-based retriever.

    Loads preprocessed document chunks from:
        data/chunks.pkl
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


    # ==========================================
    # TOKENIZATION
    # ==========================================

    def _tokenize(
        self,
        text: str
    ):

        return (
            text.lower()
            .split()
        )


    # ==========================================
    # RETRIEVE
    # ==========================================

    def retrieve(
        self,
        query: str,
        top_k: int = 10
    ):

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
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


        for index in ranked_indices[
            :top_k
        ]:

            document = (
                self.documents[index]
            )

            score = scores[index]


            results.append(

                (
                    document,
                    float(score)
                )

            )


        return results