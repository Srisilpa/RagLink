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
            rewritten_question
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

            rewritten_question,

            documents,

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
            f"Compressed: {len(selected)}"
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
        # 10. SAFETY FALLBACK
        # ==========================================

        normalized_answer = (

            answer
            .strip()
            .lower()

        )

        fallback_phrases = [

            "the answer is not explicitly stated",

            "not explicitly stated in the provided context",

            "the context does not specify",

            "the provided context does not specify",

            "i don't have enough information",

            "based on the provided context, the answer",

            "the information is not available"

        ]

        for phrase in fallback_phrases:

            if phrase in normalized_answer:

                answer = FALLBACK_ANSWER

                break

        # ==========================================
        # 11. PREPARE CHUNKS AND SOURCES
        # ==========================================

        chunks = []

        sources = []

        for document, score in selected:

            source = document.metadata.get(
                "source"
            )

            page = document.metadata.get(
                "page"
            )

            # ------------------------------
            # PREPARE CHUNK
            # ------------------------------

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

            # ------------------------------
            # ADD UNIQUE SOURCE
            # ------------------------------

            if source and source not in sources:

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