import unittest

from rag.retrieval.retriever import Retriever


class TestRetriever(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.retriever = Retriever()

    def test_leave_policy(self):
        results = self.retriever.retrieve("Leave policy")

        self.assertGreater(len(results), 0)

        content = results[0][0].page_content.lower()

        self.assertIn("leave", content)

    def test_project_alpha(self):
        results = self.retriever.retrieve("Project Alpha")

        self.assertGreater(len(results), 0)

    def test_empty_query(self):

        with self.assertRaises(ValueError):
            self.retriever.retrieve("")

    def test_random_query(self):

        results = self.retriever.retrieve("abcdefxyz")

        self.assertGreaterEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()