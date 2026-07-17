import pickle

from sklearn.metrics.pairwise import cosine_similarity

from rag.embeddings.embedding_model import get_embedding_model


class Reranker:

    def __init__(self):

        self.embedding_model = get_embedding_model()

        with open("data/chunks.pkl", "rb") as f:
            self.all_documents = pickle.load(f)

        with open("data/chunk_embeddings.pkl", "rb") as f:
            self.all_embeddings = pickle.load(f)

        # O(1) lookup
        self.embedding_lookup = {}

        for doc, embedding in zip(
            self.all_documents,
            self.all_embeddings
        ):

            self.embedding_lookup[
                doc.page_content
            ] = embedding

    def rerank(
        self,
        query,
        documents,
        top_k=5
    ):

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if not documents:
            return []

        query_embedding = self.embedding_model.embed_query(query)

        ranked = []

        for doc in documents:

            embedding = self.embedding_lookup.get(
                doc.page_content
            )

            if embedding is None:
                continue

            similarity = cosine_similarity(
                [query_embedding],
                [embedding]
            )[0][0]

            ranked.append(
                (
                    doc,
                    similarity
                )
            )

        ranked.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return [
            doc
            for doc, score in ranked[:top_k]
        ]