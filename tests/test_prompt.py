import unittest

from rag.generation.prompt import build_prompt


class TestPrompt(unittest.TestCase):

    def test_prompt_contains_question(self):

        prompt = build_prompt(
            "What is Leave Policy?",
            "Leave Policy allows..."
        )

        self.assertIn("Leave Policy", prompt)

    def test_prompt_contains_context(self):

        prompt = build_prompt(
            "Question",
            "This is context"
        )

        self.assertIn("This is context", prompt)

    def test_prompt_not_empty(self):

        prompt = build_prompt(
            "Hello",
            "World"
        )

        self.assertGreater(len(prompt), 50)


if __name__ == "__main__":
    unittest.main()