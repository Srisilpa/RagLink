import unittest

from rag.langgraph.graph import graph



class TestLangGraphTools(unittest.TestCase):


    def test_time_tool(self):

        result = graph.invoke(
            {
                "question": "What time is it?"
            }
        )

        self.assertEqual(
            result["query_type"],
            "time"
        )

        self.assertIn(
            "Current time",
            result["answer"]
        )



    def test_rag_route(self):

        result = graph.invoke(
            {
                "question":
                "What is the salary discrepancy resolution time?"
            }
        )

        self.assertEqual(
            result["query_type"],
            "rag"
        )

        self.assertIn(
            "5 working days",
            result["answer"]
        )



    def test_chat_route(self):

        result = graph.invoke(
            {
                "question":
                "hello"
            }
        )

        self.assertEqual(
            result["query_type"],
            "chat"
        )



if __name__ == "__main__":
    unittest.main()