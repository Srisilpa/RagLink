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

        query_type = classify_query(
            question
        )


        # -------------------------
        # Calculator
        # -------------------------

        if query_type == "calculator":

            return {

                "answer": calculate(question),

                "sources": [],

                "chunks": []

            }



        # -------------------------
        # Date
        # -------------------------

        if query_type == "date":

            return {

                "answer": get_date(),

                "sources": [],

                "chunks": []

            }



        # -------------------------
        # Time
        # -------------------------

        if query_type == "time":

            return {

                "answer": get_time(),

                "sources": [],

                "chunks": []

            }



        # -------------------------
        # Web Search
        # -------------------------

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
{item.get('title')}

Content:
{item.get('snippet')}
"""

                    for item in results

                ]

            )



            prompt = f"""

You are a factual assistant.

Answer ONLY using the information below.

Rules:
- Do not use your own knowledge.
- Do not guess.
- Do not add missing information.
- If information is insufficient say:
"I couldn't find reliable information."

Information:

{context}


Question:

{question}

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
                        item.get("title"),

                        "content":
                        item.get("snippet")

                    }

                    for item in results

                ]

            }



        # -------------------------
        # Internal RAG
        # -------------------------

        return self.pipeline.ask(
            question
        )