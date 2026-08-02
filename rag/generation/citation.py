"""
Citation generation utilities for RAGLink.

This module builds clean, deduplicated citations from
retrieved/reranked documents and formats them for the
final response.
"""

from typing import List, Dict, Any

from langchain_core.documents import Document


# ============================================================
# BUILD STRUCTURED SOURCES
# ============================================================

def build_sources(
    docs: List[Document],
) -> List[Dict[str, Any]]:
    """
    Build unique structured citations.

    Returns:

    [
        {
            "file": "...",
            "page": 2
        },
        ...
    ]
    """

    if not docs:
        return []

    sources = []
    seen = set()

    for doc in docs:

        if not isinstance(doc, Document):
            continue

        metadata = doc.metadata or {}

        file_name = (
            metadata.get("file_name")
            or metadata.get("source")
            or "Unknown"
        )

        page = metadata.get(
            "page_label",
            metadata.get(
                "page",
                "-"
            )
        )

        key = (
            file_name,
            page,
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "file": file_name,
                "page": page,
            }
        )

    sources.sort(
    key=lambda x: (
        x["file"],
        str(x["page"])
    )
)


# ============================================================
# FORMAT CITATIONS
# ============================================================

def format_sources(
    sources: List[Dict[str, Any]],
) -> str:
    """
    Convert structured citations into
    human-readable references.

    Example:

    Sources:
    1. Employee_Handbook.pdf (Page 5)
    2. Leave_Policy.pdf (Page 12)
    """

    if not sources:
        return ""

    lines = [
        "",
        "",
        "Sources:",
    ]

    for index, source in enumerate(
        sources,
        start=1,
    ):

        file_name = source.get(
            "file",
            "Unknown"
        )

        page = source.get(
            "page",
            "-"
        )

        lines.append(
            f"{index}. {file_name} (Page {page})"
        )

    return "\n".join(lines)


# ============================================================
# APPEND CITATIONS TO ANSWER
# ============================================================

def append_sources(
    answer: str,
    sources: List[Dict[str, Any]],
) -> str:
    """
    Append formatted citations to an answer.
    """

    if not answer:
        answer = ""

    citation_text = format_sources(sources)

    if not citation_text:
        return answer

    if "Sources:" in answer:
        return answer

    return answer.rstrip() + "\n" + citation_text