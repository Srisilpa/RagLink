import unittest

from dotenv import load_dotenv

from rag.pipeline import RAGPipeline


class TestRAGQuality(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.pipeline = RAGPipeline()

    def test_rag_answers(self):

        test_cases = [

            # Project Meridian
            (
                "What is Project Meridian?",
                "Project Meridian"
            ),

            (
                "What database does Project Meridian use?",
                "MySQL 8.0"
            ),

            (
                "What architecture does Project Meridian use?",
                "Clean Architecture"
            ),

            # Leave
            (
                "Who approves my leave request?",
                "reporting manager"
            ),

            (
                "Who approves leave longer than 5 consecutive working days?",
                "Reporting Manager"
            ),

            (
                "Can I cancel an approved leave request?",
                "HR portal"
            ),

            # Maternity Leave
            (
                "What is the maternity leave duration?",
                "26"
            ),

            # Earned Leave
            (
                "What is the maximum number of Earned Leave days an employee can carry forward?",
                "30 days"
            ),

            (
                "What happens to earned leave when I resign?",
                "encashed"
            ),

            # Remote Work
            (
                "Who approves permanent remote work requests?",
                "HR Director"
            ),

            # HR Ticketing
            (
                "What is the response SLA for HR ticketing queries?",
                "2 hours"
            ),

            # Out-of-Knowledge-Base Question
            (
                "What is the capital of France?",
                "I couldn't find that information in the company knowledge base."
            ),
        ]

        print("\n")
        print("=" * 70)
        print("RAG QUALITY EVALUATION")
        print("=" * 70)

        passed = 0
        failed = 0

        for question, expected in test_cases:

            print("\nQUESTION:")
            print(question)

            result = self.pipeline.ask(question)

            answer = result["answer"]

            print("\nANSWER:")
            print(answer)

            # Case-insensitive validation
            if expected.lower() in answer.lower():

                print("\nRESULT: PASS")
                passed += 1

            else:

                print("\nRESULT: FAIL")
                print("EXPECTED TO CONTAIN:")
                print(expected)

                failed += 1

        total = len(test_cases)

        accuracy = (
            passed / total * 100
            if total > 0
            else 0
        )

        print("\n")
        print("=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)

        print(f"Total Tests : {total}")
        print(f"Passed      : {passed}")
        print(f"Failed      : {failed}")
        print(f"Accuracy    : {accuracy:.2f}%")

        print("=" * 70)

        # Make unittest fail if any answer is incorrect
        self.assertEqual(
            failed,
            0,
            f"{failed} RAG quality test(s) failed."
        )


if __name__ == "__main__":
    unittest.main()