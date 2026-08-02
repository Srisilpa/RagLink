from rag.query_understanding.query_understanding import (
    QueryUnderstanding,
)


from rag.retrieval.retrieval_planner import (
    build_retrieval_plan,
)


from rag.retrieval.hybrid import (
    HybridRetriever,
)


from rag.retrieval.rerank import (
    Reranker,
)


from rag.generation.context import (
    build_context,
)


from rag.generation.prompt import (
    build_prompt,
)


from rag.generation.llm import (
    LLM,
)


from rag.generation.evidence_checker import (
    detect_hallucination,
    build_safe_response,
)


from rag.generation.citation import (
    build_sources,
)



FALLBACK_ANSWER = (
    "I couldn't find that information "
    "in the company knowledge base."
)





class RAGPipeline:


    def __init__(self):


        self.query_understanding = (
            QueryUnderstanding()
        )


        self.hybrid = HybridRetriever()


        self.reranker = Reranker()


        self.llm = LLM()





    # ======================================
    # CLEAN ANSWER
    # ======================================


    def clean_answer(
        self,
        answer: str
    ):


        if not answer:

            return FALLBACK_ANSWER



        answer = answer.strip()



        if not answer:

            return FALLBACK_ANSWER



        return answer






    # ======================================
    # ASK
    # ======================================


    def ask(
        self,
        question: str
    ):


        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )



        question = question.strip()



        # ======================================
        # 1. QUERY UNDERSTANDING
        # ======================================


        understanding = (

            self.query_understanding

            .understand(

                question

            )

        )



        rewritten_query = (

            understanding.get(

                "rewritten_query",

                question

            )

        )



        entities = (

            understanding.get(

                "entities",

                []

            )

        )



        intent = (

            understanding.get(

                "intent",

                "general_information"

            )

        )



        expanded_queries = (

            understanding.get(

                "expanded_queries",

                []

            )

        )



        print(
            f"Original Query: {question}"
        )


        print(
            f"Rewritten Query: {rewritten_query}"
        )


        print(
            f"Entities: {entities}"
        )


        print(
            f"Intent: {intent}"
        )



        # ======================================
        # 2. RETRIEVAL PLANNING
        # ======================================


        retrieval_plan = build_retrieval_plan(

            query=question,

            rewritten_query=rewritten_query,

            entities=entities,

            expanded_queries=expanded_queries,

            intent=intent,

        )



        print(
            "Retrieval Plan:"
        )


        print(
            retrieval_plan
        )


                # ======================================
        # 3. HYBRID RETRIEVAL
        # ======================================


        retrieved_documents = []


        for search_query in retrieval_plan.get(
            "search_queries",
            []
        ):


            results = self.hybrid.search(

                query=search_query,

                top_k=retrieval_plan.get(
                    "top_k",
                    15
                ),

                filters=retrieval_plan.get(
                    "metadata_filters",
                    {}

                )

            )


            retrieved_documents.extend(
                results
            )



        print(
            f"Retrieved candidates: "
            f"{len(retrieved_documents)}"
        )



        # ======================================
        # REMOVE DUPLICATES
        # ======================================


        unique_documents = []


        seen = set()



        for item in retrieved_documents:


            if isinstance(item, tuple):

                document, score = item

            else:

                document = item

                score = 0.0



            key = (

                document.metadata.get(
                    "source",
                    ""
                ),

                document.page_content.strip()

            )



            if key in seen:

                continue



            seen.add(key)



            unique_documents.append(

                (
                    document,

                    score

                )

            )




        if not unique_documents:


            return {

                "question":
                    question,

                "answer":
                    FALLBACK_ANSWER,

                "sources":
                    [],

                "chunks":
                    []

            }





        # ======================================
        # 4. RERANK
        # ======================================


        reranked = self.reranker.rerank(

            query=rewritten_query,

            documents=unique_documents,

            top_k=10,

            entities=entities,

            intent=intent

        )



        print(
            f"Reranked documents: {len(reranked)}"
        )




                # ======================================
        # 5. CONTEXT BUILDING
        # ======================================


        context_result = build_context(

            ranked_documents=reranked,

            max_chunks=5,

            min_score=3.0

        )



        selected = []



        # --------------------------------------
        # Handle different build_context outputs
        # --------------------------------------


        if isinstance(
            context_result,
            tuple
        ):


            context, selected = context_result



        else:


            selected = context_result



            context_parts = []



            for item in selected:



                if isinstance(
                    item,
                    tuple
                ):


                    document = item[0]



                else:


                    document = item



                context_parts.append(

                    document.page_content

                )



            context = "\n\n".join(

                context_parts

            )




        print(
            "Context built successfully"
        )



        print(
            f"Context length: {len(context)}"
        )




        if not selected:


            return {


                "question":

                    question,


                "answer":

                    FALLBACK_ANSWER,


                "sources":

                    [],


                "chunks":

                    []

            }





        # ======================================
        # 6. GENERATION
        # ======================================


        prompt = build_prompt(

            question=question,

            context=context

        )



        answer = self.llm.generate(

            prompt

        )



        answer = self.clean_answer(

            answer

        )



        # ======================================
        # 7. EVIDENCE VERIFICATION
        # ======================================


        unsupported = detect_hallucination(

            answer,

            context

        )



        if unsupported:


            print(
                "⚠️ Answer failed grounding check."
            )


            answer = build_safe_response()


                    # ======================================
        # 8. BUILD SOURCES
        # ======================================


        source_documents = []



        for item in selected:


            # Case 1:
            # (Document, score)

            if isinstance(
                item,
                tuple
            ):

                source_documents.append(
                    item[0]
                )


            # Case 2:
            # Direct Document

            else:

                source_documents.append(
                    item
                )



        sources = build_sources(

            source_documents

        )



        # fallback source creation
        # if citation builder returns empty

        if not sources:


            sources = []


            for document in source_documents:


                sources.append(

                    {

                        "source":
                            document.metadata.get(
                                "source",
                                "unknown"
                            ),


                        "page":
                            document.metadata.get(
                                "page",
                                None
                            )

                    }

                )





        # ======================================
        # 9. BUILD CHUNKS
        # ======================================


        chunks = []



        for item in selected:


            if isinstance(
                item,
                tuple
            ):


                document = item[0]

                score = item[1]



            else:


                document = item

                score = 0.0




            chunks.append(

                {

                    "content":

                        document.page_content,



                    "source":

                        document.metadata.get(

                            "source"

                        ),



                    "page":

                        document.metadata.get(

                            "page"

                        ),



                    "score":

                        round(

                            float(score),

                            4

                        )

                }

            )





        # ======================================
        # FINAL RESPONSE
        # ======================================


        return {


            "question":

                question,



            "answer":

                answer,



            "sources":

                sources,



            "chunks":

                chunks,



            "grounded":

                not unsupported

        }