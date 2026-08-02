import unittest

from rag.tools.query_router import classify_query



class TestQueryRouter(unittest.TestCase):


    def test_time_query(self):

        self.assertEqual(
            classify_query(
                "What time is it?"
            ),
            "time"
        )


    def test_date_query(self):

        self.assertEqual(
            classify_query(
                "What is today's date?"
            ),
            "date"
        )


    def test_calculator(self):

        self.assertEqual(
            classify_query(
                "25*4"
            ),
            "calculator"
        )


    def test_chat(self):

        self.assertEqual(
            classify_query(
                "hello"
            ),
            "chat"
        )


    def test_rag_time_word(self):

        self.assertEqual(
            classify_query(
                "What is salary discrepancy resolution time?"
            ),
            "rag"
        )


    def test_web(self):

        self.assertEqual(
            classify_query(
                "Who is the CEO of OpenAI?"
            ),
            "web"
        )



if __name__ == "__main__":
    unittest.main()