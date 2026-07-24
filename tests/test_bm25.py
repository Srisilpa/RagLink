import unittest

from rag.retrieval.bm25 import BM25Retriever


class TestBM25(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.retriever = BM25Retriever()

    def test_leave(self):
        docs = self.retriever.search("Leave Policy")

        self.assertGreater(
            len(docs),
            0
        )

    def test_project(self):
        docs = self.retriever.search("Project Alpha")

        self.assertGreater(
            len(docs),
            0
        )

    def test_empty(self):
        docs = self.retriever.search("")

        self.assertEqual(
            docs,
            []
        )


if __name__ == "__main__":
    unittest.main()