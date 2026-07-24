import unittest

from rag.retrieval.retriever import Retriever
from rag.retrieval.rerank import Reranker


class TestReranker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.retriever = Retriever()

        cls.reranker = Reranker()

    # ==========================================
    # LEAVE POLICY TEST
    # ==========================================

    def test_leave_policy(self):

        results = self.retriever.retrieve(
            query="Leave policy",
            return_k=5,
            fetch_k=10
        )

        self.assertGreater(
            len(results),
            0
        )

        documents = [

            document

            for document, score
            in results

        ]

        reranked = self.reranker.rerank(

            query="Leave policy",

            documents=documents,

            top_k=5

        )

        self.assertGreater(
            len(reranked),
            0
        )

        content = " ".join(

            document.page_content.lower()

            for document
            in reranked

        )

        self.assertIn(
            "leave",
            content
        )

    # ==========================================
    # PROJECT ALPHA TEST
    # ==========================================

    def test_project_alpha(self):

        results = self.retriever.retrieve(

            query="Project Alpha",

            return_k=5,

            fetch_k=10

        )

        self.assertGreater(
            len(results),
            0
        )

        documents = [

            document

            for document, score
            in results

        ]

        reranked = self.reranker.rerank(

            query="Project Alpha",

            documents=documents,

            top_k=5

        )

        self.assertGreater(
            len(reranked),
            0
        )

    # ==========================================
    # EMPTY QUERY TEST
    # ==========================================

    def test_empty_query(self):

        results = self.retriever.retrieve(

            query="Leave policy",

            return_k=5,

            fetch_k=10

        )

        documents = [

            document

            for document, score
            in results

        ]

        with self.assertRaises(
            ValueError
        ):

            self.reranker.rerank(

                query="",

                documents=documents

            )

    # ==========================================
    # EMPTY DOCUMENTS TEST
    # ==========================================

    def test_empty_documents(self):

        results = self.reranker.rerank(

            query="Leave policy",

            documents=[]

        )

        self.assertEqual(
            results,
            []
        )

    # ==========================================
    # NONE DOCUMENTS TEST
    # ==========================================

    def test_none_documents(self):

        with self.assertRaises(
            ValueError
        ):

            self.reranker.rerank(

                query="Leave policy",

                documents=None

            )


if __name__ == "__main__":

    unittest.main()