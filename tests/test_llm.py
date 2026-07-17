import unittest

from rag.generation.llm import GroqLLM


class TestGroq(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.llm = GroqLLM()

    def test_generate(self):

        response = self.llm.generate(
            "What is Artificial Intelligence?"
        )

        self.assertTrue(len(response) > 0)

    def test_math(self):

        response = self.llm.generate(
            "2 + 3 = ? Answer only."
        )

        self.assertIn("5", response)


if __name__ == "__main__":
    unittest.main()