"""
Enterprise Query Rewriter for RAGLink.

Purpose
-------
Improve retrieval quality by rewriting user queries
into concise search-friendly queries while preserving
their original meaning.

The rewriter NEVER answers the question and NEVER
adds new facts.
"""

import re

from rag.generation.llm import GroqLLM


class QueryRewriter:
    """
    Enterprise query rewriter.
    """

    MAX_QUERY_LENGTH = 250

    def __init__(self):

        self.llm = GroqLLM()

    # ========================================================
    # MAIN METHOD
    # ========================================================

    def rewrite(
        self,
        question: str,
    ) -> str:

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if not question:

            return ""

        question = question.strip()

        if not question:

            return ""

        # ----------------------------------------------------
        # Skip rewriting for short queries
        # ----------------------------------------------------

        if len(question.split()) <= 2:

            return question

        # ----------------------------------------------------
        # Prompt
        # ----------------------------------------------------

        prompt = f"""
You are an enterprise search query rewriter.

Your job is ONLY to rewrite the user's question into
a better search query.

Rules

1. NEVER answer the question.

2. NEVER invent information.

3. NEVER add technologies, products, databases,
roles, versions, names, numbers or dates that do
not already exist.

4. Preserve all important entities exactly.

5. Preserve the user's intent.

6. Remove unnecessary conversational wording.

7. Produce a concise search query.

8. Return ONLY the rewritten query.

Examples

User:
Who approves leave requests?

Output:
leave request approval authority

User:
What is Project Meridian?

Output:
Project Meridian overview

User:
What database does Project Meridian use?

Output:
Project Meridian database

User:
How long is maternity leave?

Output:
maternity leave duration

User Question:
{question}

Rewritten Query:
"""

        # ----------------------------------------------------
        # Generate
        # ----------------------------------------------------

        try:

            rewritten = self.llm.generate(prompt)

        except Exception:

            return question

        if not rewritten:

            return question

        # ----------------------------------------------------
        # Cleanup
        # ----------------------------------------------------

        rewritten = rewritten.strip()

        rewritten = rewritten.split("\n")[0]

        rewritten = rewritten.replace('"', "")

        rewritten = rewritten.replace("`", "")

        rewritten = re.sub(
            r"\s+",
            " ",
            rewritten,
        ).strip()

        # ----------------------------------------------------
        # Prevent extremely long rewrites
        # ----------------------------------------------------

        if len(rewritten) > self.MAX_QUERY_LENGTH:

            return question

        # ----------------------------------------------------
        # Prevent empty rewrites
        # ----------------------------------------------------

        if not rewritten:

            return question

        # ----------------------------------------------------
        # Don't allow drastic shortening
        # ----------------------------------------------------

        if len(rewritten.split()) < max(
            2,
            len(question.split()) // 4,
        ):

            return question

        return rewritten