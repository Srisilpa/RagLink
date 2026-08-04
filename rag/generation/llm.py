import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


class GroqLLM:

    def __init__(
        self,
        model=None,
        temperature=0.0,
    ):

        self.model = model or os.getenv(
            "MODEL_NAME",
            "llama-3.1-8b-instant"
        )

        self.temperature = temperature

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing."
            )

        self.llm = ChatGroq(
            model=self.model,
            temperature=self.temperature,
            groq_api_key=api_key,
        )

    def generate(self, prompt):

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.llm.invoke(prompt)

        return response.content.strip()


LLM = GroqLLM