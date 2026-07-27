from typing import List

from langchain_core.documents import Document

from rag.generation.llm import GroqLLM


class ContextCompressor:
    """
    Compresses retrieved documents by extracting only
    the passages relevant to the user's question.

    Input:
        List of Documents

    Output:
        Compressed context string
    """

    def __init__(self):

        self.llm = GroqLLM()

    def compress(
        self,
        query: str,
        documents: List[Document]
    ) -> str:

        # ==========================================
        # VALIDATE QUERY
        # ==========================================

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        # ==========================================
        # VALIDATE DOCUMENTS
        # ==========================================

        if not documents:

            return ""

        # ==========================================
        # BUILD DOCUMENT CONTEXT
        # ==========================================

        document_parts = []

        for index, document in enumerate(
            documents,
            start=1
        ):

            if not isinstance(
                document,
                Document
            ):

                continue

            content = (
                document.page_content
                or ""
            ).strip()

            if not content:

                continue

            document_parts.append(

                f"""
DOCUMENT {index}

SOURCE:
{document.metadata.get("file_name", "Unknown")}

CONTENT:
{content}
"""

            )

        # ==========================================
        # NO VALID DOCUMENTS
        # ==========================================

        if not document_parts:

            return ""

        documents_text = "\n".join(
            document_parts
        )

        # ==========================================
        # COMPRESSION PROMPT
        # ==========================================

        prompt = f"""
You are a context compression component
inside an enterprise Retrieval-Augmented
Generation system.

Your task is to extract ONLY the information
from the retrieved documents that is directly
relevant to answering the user's question.

USER QUESTION:
{query}

RETRIEVED DOCUMENTS:
{documents_text}

RULES:

1. Use ONLY information present in the
   retrieved documents.

2. Do NOT invent facts.

3. Do NOT add outside knowledge.

4. Preserve exact names, numbers, dates,
   versions, technologies, and technical terms.

5. Remove irrelevant information.

6. Keep important supporting details needed
   to answer the question accurately.

7. If multiple documents contain relevant
   information, combine the relevant parts.

8. If the documents do not contain information
   relevant to the question, return:

NO_RELEVANT_CONTEXT

9. Return ONLY the compressed context.

COMPRESSED CONTEXT:
"""

        compressed = self.llm.generate(
            prompt
        ).strip()

        # ==========================================
        # HANDLE EMPTY RESPONSE
        # ==========================================

        if not compressed:

            return ""

        # ==========================================
        # HANDLE NO RELEVANT CONTEXT
        # ==========================================

        if compressed == "NO_RELEVANT_CONTEXT":

            return ""

        return compressed