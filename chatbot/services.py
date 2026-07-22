from rag.pipeline import RAGPipeline

from rag.tools.query_router import classify_query

from rag.tools.calculator import calculate

from rag.tools.date import (
    get_date,
    get_time
)

from rag.tools.web_search import web_search


class ChatService:

    def __init__(self):

        self.pipeline = RAGPipeline()


    def ask(self, question):

        if not question or not question.strip():

            return {
                "answer": "Please enter a question.",
                "sources": [],
                "chunks": []
            }


        # =====================================================
        # CLASSIFY QUERY
        # =====================================================

        query_type = classify_query(
            question
        )

        print(
            f"Question: {question}"
        )

        print(
            f"Query Type: {query_type}"
        )


        # =====================================================
        # CALCULATOR
        # =====================================================

        if query_type == "calculator":

            return {

                "answer": calculate(
                    question
                ),

                "sources": [],

                "chunks": []

            }


        # =====================================================
        # DATE
        # =====================================================

        if query_type == "date":

            return {

                "answer": get_date(),

                "sources": [],

                "chunks": []

            }


        # =====================================================
        # TIME
        # =====================================================

        if query_type == "time":

            return {

                "answer": get_time(),

                "sources": [],

                "chunks": []

            }


        # =====================================================
        # WEB SEARCH
        # =====================================================

        if query_type == "web":

            results = web_search(
                question
            )


            if not results:

                return {

                    "answer":
                    "I couldn't find reliable information.",

                    "sources": [],

                    "chunks": []

                }


            context = "\n\n".join(

                [

                    f"""
Title:
{item.get('title', '')}

Content:
{item.get('snippet', '')}
"""

                    for item in results

                ]

            )


            prompt = f"""

You are a factual web search assistant.

Answer ONLY using the information provided below.

Rules:

1. Do not use your own knowledge.
2. Do not guess.
3. Do not add information that is not present.
4. If the information is insufficient, say:
"I couldn't find reliable information."

Information:

{context}

Question:

{question}

Answer:

"""


            answer = self.pipeline.generate(
                prompt
            )


            return {

                "answer": answer,

                "sources": [],

                "chunks":

                [

                    {

                        "title":
                        item.get(
                            "title",
                            ""
                        ),

                        "content":
                        item.get(
                            "snippet",
                            ""
                        )

                    }

                    for item in results

                ]

            }


        # =====================================================
        # INTERNAL RAG
        #
        # Company policies
        # HR documents
        # Projects
        # Technical documents
        # Knowledge base
        # =====================================================

        return self.pipeline.ask(
            question
        )