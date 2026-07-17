import unittest

from rag.pipeline import RAGPipeline


class TestPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pipeline = RAGPipeline()


    def test_leave(self):

        result = self.pipeline.ask(
            "What is the leave policy?"
        )

        print("\nLeave Query Result:")
        print(result)


        # Check answer exists
        self.assertIn(
            "answer",
            result
        )


        # Check sources exist
        self.assertIn(
            "sources",
            result
        )


        self.assertGreater(
            len(result["sources"]),
            0
        )


        self.assertGreater(
            len(result["answer"]),
            0
        )


    def test_empty_question(self):

        with self.assertRaises(ValueError):

            self.pipeline.ask(
                ""
            )


    def test_general_query(self):

        result = self.pipeline.ask(
            "Explain the company onboarding process."
        )

        print("\nGeneral Query Result:")
        print(result)


        self.assertIn(
            "answer",
            result
        )


        self.assertGreater(
            len(result["answer"]),
            0
        )


if __name__ == "__main__":
    unittest.main()