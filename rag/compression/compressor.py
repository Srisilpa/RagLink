from typing import List

from langchain_core.documents import Document

from rag.generation.llm import GroqLLM


class ContextCompressor:
    """
    Compress retrieved documents while preserving metadata.

    Pipeline

        Retrieved Documents
                ↓
        LLM Compression
                ↓
        Compressed Documents (metadata preserved)

    Returns:

        List[Document]
    """

    def __init__(self):

        self.llm = GroqLLM()

    # ============================================================
    # MAIN
    # ============================================================

    def compress(
        self,
        query: str,
        documents: List[Document],
    ) -> List[Document]:
        """
        Compress each retrieved document individually.

        Metadata is preserved so later stages
        (Context Refiner, Citation Generator)
        still know the original source.
        """

        # --------------------------------------------------------
        # Validate query
        # --------------------------------------------------------

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        # --------------------------------------------------------
        # Validate documents
        # --------------------------------------------------------

        if not documents:

            return []

        compressed_documents = []

        # --------------------------------------------------------
        # Compress every document independently
        # --------------------------------------------------------

        for document in documents:

            if not isinstance(
                document,
                Document,
            ):
                continue

            content = (
                document.page_content
                or ""
            ).strip()

            if not content:
                continue

            prompt = f"""
You are an enterprise RAG Context Compressor.

Your task is to extract ONLY the information
needed to answer the user's question.

QUESTION:
{query}

DOCUMENT:
{content}

RULES

1. Use ONLY information from the document.

2. Do NOT invent facts.

3. Preserve names, numbers,
dates, technologies,
and technical terminology.

4. Remove unrelated content.

5. If nothing is relevant return

NO_RELEVANT_CONTEXT

Return ONLY the compressed text.
"""

            compressed = self.llm.generate(
                prompt
            ).strip()

            # ------------------------------------
            # Ignore empty responses
            # ------------------------------------

            if not compressed:
                continue

            if (
                compressed
                == "NO_RELEVANT_CONTEXT"
            ):
                continue

            # ------------------------------------
            # Preserve metadata
            # ------------------------------------

            compressed_document = Document(

                page_content=compressed,

                metadata=document.metadata.copy(),

            )

            compressed_documents.append(
                compressed_document
            )
                    # --------------------------------------------------------
        # Compression Summary
        # --------------------------------------------------------

        print("\n" + "=" * 60)
        print("CONTEXT COMPRESSION")
        print("=" * 60)

        print(
            f"Input Documents      : {len(documents)}"
        )

        print(
            f"Compressed Documents : {len(compressed_documents)}"
        )

        print("=" * 60)

        # --------------------------------------------------------
        # Return compressed documents
        # --------------------------------------------------------

        return compressed_documents