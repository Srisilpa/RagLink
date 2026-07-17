import unittest

from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.rerank import Reranker


class TestReranker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hybrid = HybridRetriever()
        cls.reranker = Reranker()

    def test_leave_policy(self):

        docs = self.hybrid.search("Leave Policy")
        documents = [doc for doc, _ in docs]

        ranked = self.reranker.rerank(
            "Leave Policy",
            documents
        )

        self.assertGreater(len(ranked), 0)

    def test_project_alpha(self):

        docs = self.hybrid.search("Project Alpha")
        documents = [doc for doc, _ in docs]

        ranked = self.reranker.rerank(
            "Project Alpha",
            documents
        )

        self.assertGreater(len(ranked), 0)

    def test_empty_query(self):

        with self.assertRaises(ValueError):
            self.reranker.rerank("", [])


if __name__ == "__main__":
    unittest.main()