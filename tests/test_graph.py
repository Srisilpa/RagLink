import unittest

from rag.langgraph.graph import graph


class TestGraph(unittest.TestCase):

    def test_graph_created(self):
        self.assertIsNotNone(graph)

    def test_graph_has_nodes(self):
        self.assertIsNotNone(graph)


if __name__ == "__main__":
    unittest.main()