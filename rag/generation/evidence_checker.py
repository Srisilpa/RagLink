"""
Evidence checking for RAGLink.

This module performs a basic first-level evidence check.

Important distinction:

    Retrieved context exists
        !=
    Retrieved context necessarily contains the answer

This module currently checks whether usable context
was retrieved.

A stronger answer-level evidence check can be added
later after retrieval and context refinement are stable.
"""


from typing import List


# ============================================================
# SAFE FALLBACK RESPONSE
# ============================================================

SAFE_NOT_FOUND_RESPONSE = (
    "I couldn't find that information "
    "in the company knowledge base."
)


# ============================================================
# CHECK RETRIEVED CONTEXT
# ============================================================

def has_retrieved_context(
    contexts: List[str],
) -> bool:
    """
    Check whether usable context was retrieved.

    Args:
        contexts:
            List of retrieved or refined context strings.

    Returns:
        True if at least one non-empty context exists.
        False otherwise.
    """

    if not contexts:

        return False

    valid_contexts = [

        context.strip()

        for context in contexts

        if context
        and isinstance(
            context,
            str,
        )
        and context.strip()

    ]

    return len(
        valid_contexts
    ) > 0


# ============================================================
# BUILD SAFE RESPONSE
# ============================================================

def build_safe_response() -> str:
    """
    Return the standard grounded fallback response.
    """

    return SAFE_NOT_FOUND_RESPONSE