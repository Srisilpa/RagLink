from rag.generation.llm import LLM
from rag.generation.prompt import build_prompt



class Generator:

    def __init__(self):

        self.llm = LLM()


    def generate(
            self,
            question: str,
            documents
    ):

        context = "\n\n".join(
            [
                doc.page_content
                for doc in documents
            ]
        )


        prompt = build_prompt(
            question,
            context
        )


        answer = self.llm.generate(
            prompt
        )


        sources = [
            doc.metadata.get("source")
            for doc in documents
        ]


        return {
            "answer": answer,
            "sources": sources
        }