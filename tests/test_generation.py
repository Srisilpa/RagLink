import unittest

from rag.generation.generator import Generator



class FakeDocument:

    def __init__(self,text):

        self.page_content=text

        self.metadata={
            "source":
            "HR_Division_Knowledge_Base.docx"
        }



class TestGenerator(unittest.TestCase):


    def test_generation(self):

        docs=[
            FakeDocument(
                """
                Leave requests are submitted
                through HR Connect.
                """
            )
        ]


        generator=Generator()


        response=generator.generate(
            "How to apply leave?",
            docs
        )


        print(response)


        self.assertIn(
            "answer",
            response
        )


if __name__=="__main__":
    unittest.main()