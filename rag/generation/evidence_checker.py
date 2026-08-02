"""
Evidence checking utilities for RAGLink.

Pipeline

Retrieved Context
        ↓
Evidence Availability Check
        ↓
Generated Answer
        ↓
Grounding Verification
        ↓
Safe / Unsupported

This module is intentionally lightweight.
It does not use another LLM, making it fast
enough for production deployments.
"""

import re
from typing import Dict, List


# ============================================================
# SAFE FALLBACK RESPONSE
# ============================================================

SAFE_NOT_FOUND_RESPONSE = (
    "I couldn't find that information "
    "in the company knowledge base."
)


# ============================================================
# SAFE RESPONSE
# ============================================================

def build_safe_response() -> str:
    """
    Return the standard fallback response.
    """

    return SAFE_NOT_FOUND_RESPONSE


# ============================================================
# RETRIEVED CONTEXT CHECK
# ============================================================

def has_retrieved_context(
    contexts: List[str],
) -> bool:
    """
    Returns True if at least one usable
    context string exists.
    """

    if not contexts:
        return False

    return any(

        isinstance(context, str)
        and context.strip()

        for context in contexts

    )


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

STOPWORDS = {

    "the",
    "is",
    "are",
    "was",
    "were",
    "a",
    "an",
    "of",
    "to",
    "for",
    "and",
    "or",
    "in",
    "on",
    "at",
    "by",
    "with",
    "from",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its",
    "be",
    "as",
    "into",
    "about",
    "can",
    "could",
    "should",
    "would",
    "will",
    "may",
    "might",
    "if",
    "then",
    "than",
    "do",
    "does",
    "did",
    "doing",
    "have",
    "has",
    "had",
    "having",
    "use",
    "used",
    "using",
    "what",
    "when",
    "where",
    "why",
    "who",
    "which",
    "how",

}


def _keywords(
    text: str,
) -> set:
    """
    Extract meaningful lowercase keywords.
    """

    if not text:
        return set()

    words = re.findall(

        r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",

        text.lower(),

    )

    return {

        word

        for word in words

        if len(word) > 2
        and word not in STOPWORDS

    }


# ============================================================
# ANSWER GROUNDING
# ============================================================

def verify_answer_grounding(
    answer: str,
    context: str,
    minimum_overlap: float = 0.25,
) -> Dict:
    """
    Verify that the generated answer is
    sufficiently grounded in the retrieved
    context.

    Returns:

    {
        "supported": bool,
        "overlap_ratio": float,
        "matched_keywords": int,
        "answer_keywords": int
    }
    """

    if not answer or not context:

        return {

            "supported": False,
            "overlap_ratio": 0.0,
            "matched_keywords": 0,
            "answer_keywords": 0,

        }

    answer_words = _keywords(answer)

    context_words = _keywords(context)

    if not answer_words:

        return {

            "supported": False,
            "overlap_ratio": 0.0,
            "matched_keywords": 0,
            "answer_keywords": 0,

        }

    overlap = answer_words & context_words

    overlap_ratio = (

        len(overlap)

        /

        len(answer_words)

    )

    return {

        "supported":

            overlap_ratio >= minimum_overlap,

        "overlap_ratio":

            round(overlap_ratio, 3),

        "matched_keywords":

            len(overlap),

        "answer_keywords":

            len(answer_words),

    }


# ============================================================
# HALLUCINATION CHECK
# ============================================================

def detect_hallucination(
    answer: str,
    context: str,
    minimum_overlap: float = 0.25,
) -> bool:
    """
    Returns True if the answer appears to
    contain unsupported information.
    """

    result = verify_answer_grounding(

        answer=answer,
        context=context,
        minimum_overlap=minimum_overlap,

    )

    return not result["supported"]


# ============================================================
# FINAL ANSWER VALIDATION
# ============================================================

def validate_answer(
    answer: str,
    context: str,
) -> str:
    """
    Final validation before returning
    the answer to the user.

    If the answer is not sufficiently
    grounded, return the standard
    safe fallback response.
    """

    if not answer:

        return build_safe_response()

    if detect_hallucination(

        answer,
        context,

    ):

        return build_safe_response()

    return answer