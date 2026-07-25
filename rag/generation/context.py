from typing import List, Tuple

from langchain_core.documents import Document


def build_context(
    ranked_documents: List[Tuple[Document, float]],
    max_chunks: int = 5,
    min_score: float = -2.0
):
    """
    Build a clean context from reranked documents.

    Args:
        ranked_documents:
            List of (Document, relevance_score) tuples.

        max_chunks:
            Maximum number of chunks to include.

        min_score:
            Minimum reranker score allowed.

    Returns:
        context:
            String containing selected document chunks.

        selected:
            List of (Document, score) tuples.
    """

    if not ranked_documents:
        return "", []

    if max_chunks <= 0:
        return "", []

    # =========================================================
    # REMOVE INVALID DOCUMENTS
    # =========================================================

    valid_documents = []

    for document, score in ranked_documents:

        if document is None:
            continue

        if not document.page_content:
            continue

        content = document.page_content.strip()

        if not content:
            continue

        valid_documents.append(
            (
                document,
                float(score)
            )
        )

    if not valid_documents:
        return "", []

    # =========================================================
    # REMOVE DUPLICATE CONTENT
    # =========================================================

    unique_documents = []

    seen_content = set()

    for document, score in valid_documents:

        normalized_content = " ".join(
            document.page_content.lower().split()
        )

        if normalized_content in seen_content:
            continue

        seen_content.add(
            normalized_content
        )

        unique_documents.append(
            (
                document,
                score
            )
        )

    # =========================================================
    # SELECT RELEVANT DOCUMENTS
    # =========================================================

    selected = []

    for document, score in unique_documents:

        if score < min_score:
            continue

        selected.append(
            (
                document,
                score
            )
        )

        if len(selected) >= max_chunks:
            break

    # =========================================================
    # FALLBACK
    # =========================================================

    # If the threshold removed everything, use the best result.
    # This prevents valid answers from being lost because of
    # a strict cross-encoder score.
    if not selected:

        selected = unique_documents[
            :min(
                max_chunks,
                len(unique_documents)
            )
        ]

    # =========================================================
    # BUILD CONTEXT
    # =========================================================

    context_parts = []

    for index, (
        document,
        score
    ) in enumerate(
        selected,
        start=1
    ):

        source = document.metadata.get(
            "source",
            "Unknown source"
        )

        page = document.metadata.get(
            "page"
        )

        if page is not None:

            source_info = (
                f"{source}, page {page}"
            )

        else:

            source_info = source

        context_parts.append(

            f"[Context {index}]\n"
            f"Source: {source_info}\n"
            f"Content:\n"
            f"{document.page_content.strip()}"

        )

    context = "\n\n".join(
        context_parts
    )

    print(
        f"Final Context Chunks: "
        f"{len(selected)}"
    )

    return context, selected