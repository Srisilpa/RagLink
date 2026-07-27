from rag.generation.llm import LLM


class QueryRewriter:
    """
    Rewrites user queries to improve retrieval quality
    while preserving the original intent and entities.

    Important:
    The rewriter must NEVER answer the question
    or introduce facts that are not present in the query.
    """

    def __init__(self):

        self.llm = LLM()

    def rewrite(
        self,
        question: str
    ) -> str:

        # ==========================================
        # VALIDATE INPUT
        # ==========================================

        question = question.strip()

        if not question:

            return question

        # ==========================================
        # QUERY REWRITING PROMPT
        # ==========================================

        prompt = f"""
You are a query rewriting component for an enterprise
RAG retrieval system.

Your task is to rewrite the user's question into a
better search query for retrieving relevant documents
from a company knowledge base.

IMPORTANT RULES:

1. Preserve the exact meaning and intent of the
   original question.

2. NEVER answer the question.

3. NEVER introduce facts that are not explicitly
   present in the original question.

4. NEVER guess an answer.

5. NEVER add specific values, names, products,
   technologies, databases, prices, dates, or roles
   unless they already appear in the original question.

6. Preserve important entity names exactly.

7. Preserve important keywords exactly.

8. Preserve the question type.

   For example:
   "Who" → preserve the person/role/authority intent.

   "What database" → preserve the database intent.

   "When" → preserve the time/date intent.

   "How much" → preserve the price/cost intent.

   "How long" → preserve the duration intent.

9. Remove unnecessary conversational words when
   appropriate.

10. Add useful search terminology ONLY if it is a
    direct paraphrase of the original question.

11. Do not change the scope of the question.

12. Keep the rewritten query concise.

13. Return ONLY the rewritten query.

EXAMPLES:

Original:
What is Project Meridian?

Rewritten:
Project Meridian definition

Original:
Who approves my leave request?

Rewritten:
leave request approval authority

Original:
What database does Project Meridian use?

Rewritten:
Project Meridian database

Original:
What is the maternity leave duration?

Rewritten:
maternity leave duration

Original:
What is the exact monthly subscription price
for the B2B SaaS license?

Rewritten:
B2B SaaS license exact monthly subscription price

Original:
What happens to earned leave when I resign?

Rewritten:
earned leave resignation encashment

Original:
How do I deploy Project Alpha?

Rewritten:
Project Alpha deployment procedure

Original:
What is the SLA for resolving critical incidents?

Rewritten:
critical incident SLA resolution time

USER QUESTION:
{question}

REWRITTEN QUERY:
"""

        # ==========================================
        # GENERATE REWRITTEN QUERY
        # ==========================================

        rewritten = self.llm.generate(
            prompt
        ).strip()

        # ==========================================
        # FALLBACK
        # ==========================================

        if not rewritten:

            return question

        # ==========================================
        # SAFETY CHECK
        # ==========================================

        # Prevent accidental multi-line responses.
        rewritten = rewritten.split(
            "\n"
        )[0].strip()

        return rewritten