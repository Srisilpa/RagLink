import pickle

from rank_bm25 import BM25Okapi


CHUNK_PATH = "data/chunks.pkl"


class BM25Retriever:

    def __init__(self):

        with open(CHUNK_PATH, "rb") as f:
            self.documents = pickle.load(f)

        self.corpus = [
            doc.page_content.split()
            for doc in self.documents
        ]

        self.bm25 = BM25Okapi(self.corpus)

    def search(self, query, k=5):

        tokens = query.split()

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:k]