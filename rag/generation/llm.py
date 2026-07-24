import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


class GroqLLM:
    """
    Wrapper around the Groq LLM.

    Provides a simple generate(prompt) API
    for the RAG pipeline and LangGraph nodes.
    """

    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.0
    ):

        self.model = model
        self.temperature = temperature

        # ==========================================
        # GET GROQ API KEY
        # ==========================================

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Please add GROQ_API_KEY to your .env file."
            )

        # ==========================================
        # INITIALIZE GROQ
        # ==========================================

        self.llm = ChatGroq(

            model=self.model,

            temperature=self.temperature,

            groq_api_key=api_key

        )

    # ==========================================
    # GENERATE
    # ==========================================

    def generate(
        self,
        prompt: str
    ) -> str:
        """
        Generate an answer using Groq.

        Args:
            prompt:
                Prompt containing the question
                and retrieved context.

        Returns:
            Generated answer as a string.

        Raises:
            ValueError:
                If prompt is empty.
        """

        # ==========================================
        # VALIDATE PROMPT
        # ==========================================

        if not prompt or not prompt.strip():

            raise ValueError(
                "Prompt cannot be empty."
            )

        # ==========================================
        # CALL GROQ
        # ==========================================

        response = self.llm.invoke(
            prompt
        )

        # ==========================================
        # EXTRACT CONTENT
        # ==========================================

        if hasattr(
            response,
            "content"
        ):

            return response.content.strip()

        return str(
            response
        ).strip()


# ==========================================
# BACKWARD COMPATIBILITY
# ==========================================

# Existing pipeline code uses:
#
#     from rag.generation.llm import LLM
#
# LangGraph code uses:
#
#     from rag.generation.llm import GroqLLM
#
# Both now point to the same implementation.

LLM = GroqLLM