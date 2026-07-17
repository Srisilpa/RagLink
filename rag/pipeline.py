from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.rerank import Reranker

from rag.generation.prompt import build_prompt
from rag.generation.llm import LLM


class RAGPipeline:

    def __init__(self):

        self.hybrid = HybridRetriever()
        self.reranker = Reranker()
        self.llm = LLM()


    def ask(self, question: str):

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )


        retrieved = self.hybrid.search(
            question
        )


        documents = [
            doc
            for doc, score in retrieved
        ]


        ranked = self.reranker.rerank(
            question,
            documents,
            top_k=5
        )


        context = "\n\n".join(
            doc.page_content
            for doc in ranked
        )


        prompt = build_prompt(
            context=context,
            question=question
        )


        answer = self.llm.generate(
            prompt
        )


        # Remove duplicate sources
        sources = []

        seen = set()

        for doc in ranked:

            source = doc.metadata.get(
                "source"
            )

            if source not in seen:

                seen.add(source)

                sources.append(
                    {
                        "file": source,
                        "page": doc.metadata.get(
                            "page"
                        )
                    }
                )


        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }