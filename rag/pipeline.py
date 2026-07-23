from rag.retrieval.hybrid import (
    HybridRetriever
)

from rag.retrieval.rerank import (
    Reranker
)

from rag.generation.context import (
    ContextBuilder
)

from rag.generation.prompt import (
    build_prompt
)

from rag.generation.llm import (
    LLM
)


class RAGPipeline:

    def __init__(self):

        self.hybrid = (
            HybridRetriever()
        )

        self.reranker = (
            Reranker()
        )

        self.context_builder = (
            ContextBuilder()
        )

        self.llm = (
            LLM()
        )


    # ==============================================
    # GENERATE
    # ==============================================

    def generate(
        self,
        prompt: str
    ):

        return self.llm.generate(
            prompt
        )


    # ==============================================
    # ASK
    # ==============================================

    def ask(
        self,
        question: str
    ):

        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )


        # ==========================================
        # STEP 1: HYBRID RETRIEVAL
        # ==========================================

        retrieved = (

            self.hybrid.search(

                query=question,

                top_k=10

            )

        )


        # ==========================================
        # NO RESULTS
        # ==========================================

        if not retrieved:

            return {

                "question":
                question,

                "answer":
                "I couldn't find that information in the company knowledge base.",

                "sources":
                [],

                "chunks":
                []

            }


        # ==========================================
        # STEP 2: EXTRACT DOCUMENTS
        # ==========================================

        documents = [

            doc

            for doc, score

            in retrieved

        ]


        # ==========================================
        # STEP 3: RERANK
        # ==========================================

        ranked = (

            self.reranker.rerank(

                query=question,

                documents=documents,

                top_k=5

            )

        )


        # ==========================================
        # STEP 4: BUILD CONTEXT
        # ==========================================

        context = (

            self.context_builder.build(

                ranked,

                max_documents=5

            )

        )


        # ==========================================
        # NO CONTEXT
        # ==========================================

        if not context.strip():

            return {

                "question":
                question,

                "answer":
                "I couldn't find that information in the company knowledge base.",

                "sources":
                [],

                "chunks":
                []

            }


        # ==========================================
        # STEP 5: BUILD PROMPT
        # ==========================================

        prompt = build_prompt(

            context=context,

            question=question

        )


        # ==========================================
        # STEP 6: GENERATE ANSWER
        # ==========================================

        answer = (

            self.llm.generate(

                prompt

            )

        )


        # ==========================================
        # STEP 7: RETURN CHUNKS
        # ==========================================

        chunks = [

            {

                "content":
                doc.page_content,

                "source":
                doc.metadata.get(
                    "source"
                ),

                "page":
                doc.metadata.get(
                    "page"
                )

            }

            for doc in ranked

        ]


        return {

            "question":
            question,

            "answer":
            answer,

            "sources":
            [],

            "chunks":
            chunks

        }