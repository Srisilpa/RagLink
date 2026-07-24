from typing import List, Tuple

from langchain_core.documents import Document


def compress_context(
    ranked_documents: List[Tuple[Document, float]],
    max_chunks: int = 5,
    min_score: float = 3.0
) -> List[Tuple[Document, float]]:
    """
    Select the most relevant documents after reranking.

    Steps:
    1. Validate Document objects.
    2. Remove empty documents.
    3. Remove duplicate content.
    4. Remove low-score documents.
    5. Keep at most max_chunks documents.
    """

    selected = []

    seen = set()

    for document, score in ranked_documents:

        # --------------------------------
        # Validate document
        # --------------------------------

        if not isinstance(
            document,
            Document
        ):

            continue

        content = (
            document.page_content.strip()
        )

        if not content:

            continue

        # --------------------------------
        # Convert score to float
        # --------------------------------

        try:

            score = float(
                score
            )

        except (
            TypeError,
            ValueError
        ):

            continue

        # --------------------------------
        # Remove low relevance results
        # --------------------------------

        if score < min_score:

            continue

        # --------------------------------
        # Normalize content
        # --------------------------------

        normalized = (
            " ".join(
                content.lower().split()
            )
        )

        # --------------------------------
        # Remove duplicates
        # --------------------------------

        if normalized in seen:

            continue

        seen.add(
            normalized
        )

        # --------------------------------
        # Add selected document
        # --------------------------------

        selected.append(

            (
                document,
                score
            )

        )

        # --------------------------------
        # Maximum chunks
        # --------------------------------

        if len(selected) >= max_chunks:

            break

    return selected


def build_context(
    ranked_documents: List[Tuple[Document, float]],
    max_chunks: int = 5,
    min_score: float = 3.0
):

    selected = compress_context(

        ranked_documents=ranked_documents,

        max_chunks=max_chunks,

        min_score=min_score

    )

    context_parts = []

    for index, (
        document,
        score
    ) in enumerate(

        selected,

        start=1

    ):

        context_parts.append(

            f"[Context {index}]\n"
            f"{document.page_content.strip()}"

        )

    context = "\n\n".join(
        context_parts
    )

    return (
        context,
        selected
    )