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

        # --------------------------------
        # Build context
        # --------------------------------

        context = "\n\n".join(
            [
                doc.page_content
                for doc in documents
                if doc.page_content
            ]
        )

        # --------------------------------
        # Build prompt
        # --------------------------------

        prompt = build_prompt(
            question=question,
            context=context
        )

        # --------------------------------
        # Generate answer
        # --------------------------------

        answer = self.llm.generate(
            prompt
        )

        # --------------------------------
        # Collect sources
        # --------------------------------

        sources = [
            doc.metadata.get(
                "source"
            )
            for doc in documents
        ]

        return {
            "answer": answer,
            "sources": sources
        }