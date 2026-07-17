import unittest

from rag.retrieval.hybrid import HybridRetriever


class TestHybridRetriever(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hybrid = HybridRetriever()

    def test_leave(self):

        docs = self.hybrid.search("Leave Policy")

        self.assertGreater(len(docs), 0)

    def test_project(self):

        docs = self.hybrid.search("Project Alpha")

        self.assertGreater(len(docs), 0)

    def test_empty_query(self):

        with self.assertRaises(ValueError):
            self.hybrid.search("")


if __name__ == "__main__":
    unittest.main()