import unittest

from rag.pipeline import RAGPipeline


class TestPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.pipeline = RAGPipeline()

    # ==========================================
    # LEAVE POLICY
    # ==========================================

    def test_leave(self):

        result = self.pipeline.ask(
            "What is the leave policy?"
        )

        print(
            "\nLeave Query Result:"
        )

        print(
            result
        )

        # Check result structure

        self.assertIn(
            "question",
            result
        )

        self.assertIn(
            "answer",
            result
        )

        self.assertIn(
            "sources",
            result
        )

        self.assertIn(
            "chunks",
            result
        )

        # Check answer exists

        self.assertGreater(
            len(result["answer"]),
            0
        )

        # Check sources exist

        self.assertGreater(
            len(result["sources"]),
            0
        )

        # Check chunks exist

        self.assertGreater(
            len(result["chunks"]),
            0
        )

    # ==========================================
    # EMPTY QUESTION
    # ==========================================

    def test_empty_question(self):

        with self.assertRaises(
            ValueError
        ):

            self.pipeline.ask(
                ""
            )

    # ==========================================
    # WHITESPACE QUESTION
    # ==========================================

    def test_whitespace_question(self):

        with self.assertRaises(
            ValueError
        ):

            self.pipeline.ask(
                "   "
            )

    # ==========================================
    # GENERAL QUERY
    # ==========================================

    def test_general_query(self):

        result = self.pipeline.ask(

            "Explain the company onboarding process."

        )

        print(
            "\nGeneral Query Result:"
        )

        print(
            result
        )

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