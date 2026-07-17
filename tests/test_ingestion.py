import os
import pickle
import unittest


class TestIngestion(unittest.TestCase):

    def test_chunk_file_exists(self):
        self.assertTrue(os.path.exists("data/chunks.pkl"))

    def test_chunk_file_not_empty(self):

        with open("data/chunks.pkl", "rb") as f:
            chunks = pickle.load(f)

        self.assertGreater(len(chunks), 0)

    def test_first_chunk(self):

        with open("data/chunks.pkl", "rb") as f:
            chunks = pickle.load(f)

        self.assertTrue(hasattr(chunks[0], "page_content"))


if __name__ == "__main__":
    unittest.main()