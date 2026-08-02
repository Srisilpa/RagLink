from typing import List, Tuple

from langchain_core.documents import Document


def build_context(
    ranked_documents: List[Tuple[Document, float]],
    max_chunks: int = 5,
    min_score: float = -2.0
):
    """
    Build a clean context from reranked documents.

    Improvements:
    --------------------
    ✓ Dynamic threshold
    ✓ Duplicate removal
    ✓ Page diversification
    ✓ Better fallback
    ✓ Cleaner context
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
    # REMOVE DUPLICATES
    # =========================================================

    unique_documents = []

    seen = set()

    for document, score in valid_documents:

        normalized_content = " ".join(
            document.page_content.lower().split()
        )

        key = (
            document.metadata.get("source"),
            normalized_content
        )

        if key in seen:
            continue

        seen.add(key)

        unique_documents.append(
            (
                document,
                score
            )
        )

    # =========================================================
    # DYNAMIC SCORE THRESHOLD
    # =========================================================

    top_score = unique_documents[0][1]

    dynamic_threshold = max(
        min_score,
        top_score * 0.75
    )

    # =========================================================
    # SELECT DOCUMENTS
    # =========================================================

    selected = []

    seen_pages = set()

    for document, score in unique_documents:

        if score < dynamic_threshold:
            continue

        page_key = (
            document.metadata.get("source"),
            document.metadata.get("page")
        )

        # Prefer diversity across pages
        if page_key in seen_pages:
            continue

        seen_pages.add(page_key)

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

    if not selected:

        selected = unique_documents[
            :min(max_chunks, len(unique_documents))
        ]

    # =========================================================
    # BUILD CONTEXT
    # =========================================================

    context_parts = []

    for index, (document, score) in enumerate(
        selected,
        start=1
    ):

        source = document.metadata.get(
            "source",
            "Unknown source"
        )

        page = document.metadata.get("page")

        if page is not None:
            source_info = f"{source}, Page {page}"
        else:
            source_info = source

        content = document.page_content.strip()

        # Prevent very long chunks
        if len(content) > 1200:
            content = content[:1200] + "..."

        context_parts.append(

            f"[Context {index}]\n"
            f"Source: {source_info}\n"
            f"Relevance Score: {score:.2f}\n"
            f"Content:\n"
            f"{content}"

        )

    context = "\n\n".join(context_parts)

    print("\n========== CONTEXT ==========")
    print(f"Dynamic Threshold : {dynamic_threshold:.2f}")
    print(f"Selected Chunks   : {len(selected)}")

    for i, (doc, score) in enumerate(selected, start=1):

        print(
            f"{i}. "
            f"{doc.metadata.get('source')} | "
            f"Page {doc.metadata.get('page')} | "
            f"Score={score:.2f}"
        )

    print("=============================\n")

    return selected