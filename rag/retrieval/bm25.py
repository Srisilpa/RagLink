import os
import pickle

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    BM25 keyword-based retriever.

    Loads preprocessed document chunks from:
        data/chunks.pkl

    Supports:
        - retrieve(query, top_k)
        - search(query, top_k)

    Both methods return:
        [(document, score), ...]
    """

    def __init__(
        self,
        chunks_path: str = "data/chunks.pkl"
    ):

        self.chunks_path = chunks_path

        # ==========================================
        # CHECK FILE
        # ==========================================

        if not os.path.exists(self.chunks_path):

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

    # ==========================================
    # TOKENIZATION
    # ==========================================

    def _tokenize(
        self,
        text: str
    ):
        """
        Convert text into lowercase tokens.

        Example:

        "Leave Policy"

        becomes:

        ["leave", "policy"]
        """

        if not text:

            return []

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
        """
        Retrieve the most relevant documents
        using BM25 keyword matching.

        Returns:

            [(document, score), ...]

        For an empty query, returns an empty list.
        """

        # ==========================================
        # HANDLE EMPTY QUERY
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

            key=lambda i: scores[i],

            reverse=True

        )

        # ==========================================
        # BUILD RESULTS
        # ==========================================

        results = []

        for index in ranked_indices[:top_k]:

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

    # ==========================================
    # SEARCH
    # ==========================================

    def search(
        self,
        query: str,
        top_k: int = 10
    ):
        """
        Backward-compatible search method.

        Older tests and modules may call:

            retriever.search(query)

        The main implementation uses:

            retriever.retrieve(query)

        Both return the same result format.
        """

        return self.retrieve(
            query=query,
            top_k=top_k
        )