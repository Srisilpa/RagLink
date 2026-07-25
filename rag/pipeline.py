from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.rerank import Reranker

from rag.generation.context import build_context
from rag.generation.prompt import build_prompt
from rag.generation.llm import LLM
from rag.generation.query_rewriter import QueryRewriter


FALLBACK_ANSWER = (
    "I couldn't find that information "
    "in the company knowledge base."
)


class RAGPipeline:

    def __init__(self):

        # --------------------------------
        # Query Rewriter
        # --------------------------------

        self.query_rewriter = QueryRewriter()

        # --------------------------------
        # Hybrid Retriever
        # --------------------------------

        self.hybrid = HybridRetriever()

        # --------------------------------
        # Cross Encoder Reranker
        # --------------------------------

        self.reranker = Reranker()

        # --------------------------------
        # LLM
        # --------------------------------

        self.llm = LLM()

    # ==========================================
    # GENERATE
    # ==========================================

    def generate(
        self,
        prompt: str
    ):

        if not prompt or not prompt.strip():

            raise ValueError(
                "Prompt cannot be empty."
            )

        return self.llm.generate(
            prompt
        )

    # ==========================================
    # CLEAN ANSWER
    # ==========================================

    def clean_answer(
        self,
        answer: str
    ):
        """
        Cleans unwanted fallback text that the LLM may
        accidentally append to an otherwise valid answer.
        """

        if not answer:
            return FALLBACK_ANSWER

        answer = answer.strip()

        # ------------------------------------------
        # Fallback variants
        # ------------------------------------------

        fallback_variants = [

            "I couldn't find that information "
            "in the company knowledge base.",

            "I could not find that information "
            "in the company knowledge base.",

            "I couldn't find that information "
            "in the company knowledge base",

            "I could not find that information "
            "in the company knowledge base"

        ]

        # ------------------------------------------
        # Check whether the answer contains fallback
        # ------------------------------------------

        answer_lower = answer.lower()

        for fallback in fallback_variants:

            fallback_lower = fallback.lower()

            if fallback_lower in answer_lower:

                # ----------------------------------
                # Find fallback position
                # ----------------------------------

                fallback_position = (
                    answer_lower.find(
                        fallback_lower
                    )
                )

                # ----------------------------------
                # Text before fallback
                # ----------------------------------

                before_fallback = (
                    answer[
                        :fallback_position
                    ].strip()
                )

                # ----------------------------------
                # If meaningful answer exists,
                # remove the appended fallback.
                # ----------------------------------

                if before_fallback:

                    answer = before_fallback

                else:

                    answer = FALLBACK_ANSWER

                break

        # ==========================================
        # REMOVE UNNECESSARY PREFIXES
        # ==========================================

        unwanted_prefixes = [

            "ANSWER:",

            "Answer:",

            "ANSWER :",

            "Answer :"

        ]

        for prefix in unwanted_prefixes:

            if answer.startswith(prefix):

                answer = answer[
                    len(prefix):
                ].strip()

                break

        # ==========================================
        # FINAL FALLBACK
        # ==========================================

        if not answer:

            return FALLBACK_ANSWER

        return answer

    # ==========================================
    # ASK
    # ==========================================

    def ask(
        self,
        question: str
    ):

        # --------------------------------
        # VALIDATE QUESTION
        # --------------------------------

        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        # --------------------------------
        # CLEAN QUESTION
        # --------------------------------

        question = question.strip()

        # ==========================================
        # 1. QUERY REWRITING
        # ==========================================

        rewritten_question = (
            self.query_rewriter.rewrite(
                question
            )
        )

        print(
            f"Original Query: {question}"
        )

        print(
            f"Rewritten Query: {rewritten_question}"
        )

        # ==========================================
        # 2. HYBRID RETRIEVAL
        # ==========================================

        retrieved = self.hybrid.search(

            rewritten_question,

            top_k=15

        )

        print(
            f"Retrieved: {len(retrieved)}"
        )

        # ==========================================
        # 3. EXTRACT DOCUMENTS
        # ==========================================

        documents = [

            document

            for document, score

            in retrieved

        ]

        # ==========================================
        # 4. NO DOCUMENTS
        # ==========================================

        if not documents:

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

        # ==========================================
        # 5. RERANKING
        # ==========================================

        reranked = self.reranker.rerank(

            query=rewritten_question,

            documents=documents,

            top_k=10

        )

        print(
            f"Reranked: {len(reranked)}"
        )

        # ==========================================
        # 6. CONTEXT COMPRESSION
        # ==========================================

        context, selected = build_context(

            ranked_documents=reranked,

            max_chunks=5,

            min_score=3.0

        )

        print(
            f"Final Context Chunks: "
            f"{len(selected)}"
        )

        # ==========================================
        # 7. NO USEFUL CONTEXT
        # ==========================================

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

        # ==========================================
        # 8. BUILD PROMPT
        # ==========================================

        prompt = build_prompt(

            question=question,

            context=context

        )

        # ==========================================
        # 9. GENERATE ANSWER
        # ==========================================

        answer = self.llm.generate(
            prompt
        )

        # ==========================================
        # 10. CLEAN ANSWER
        # ==========================================

        answer = self.clean_answer(
            answer
        )

        # ==========================================
        # 11. PREPARE CHUNKS AND SOURCES
        # ==========================================

        chunks = []

        sources = []

        for document, score in selected:

            # --------------------------------------
            # SOURCE
            # --------------------------------------

            source = document.metadata.get(
                "source"
            )

            # --------------------------------------
            # PAGE
            # --------------------------------------

            page = document.metadata.get(
                "page"
            )

            # --------------------------------------
            # PREPARE CHUNK
            # --------------------------------------

            chunks.append(

                {

                    "content":
                        document.page_content,

                    "source":
                        source,

                    "page":
                        page,

                    "score":
                        round(
                            float(score),
                            4
                        )

                }

            )

            # --------------------------------------
            # ADD UNIQUE SOURCE
            # --------------------------------------

            if (

                source

                and

                source not in sources

            ):

                sources.append(
                    source
                )

        # ==========================================
        # 12. RETURN RESULT
        # ==========================================

        return {

            "question":
                question,

            "answer":
                answer,

            "sources":
                sources,

            "chunks":
                chunks

        }