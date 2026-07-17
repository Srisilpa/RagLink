import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


class GroqLLM:
    """
    Wrapper around the Groq LLM.
    """

    def __init__(self):

        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
        )

    def generate(self, prompt: str) -> str:

        response = self.llm.invoke(prompt)
        return response.content


# Alias so older code importing LLM also works.
LLM = GroqLLM