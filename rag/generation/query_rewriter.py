from rag.generation.llm import LLM


class QueryRewriter:

    def __init__(self):
        self.llm = LLM()

    def rewrite(self, question: str) -> str:

        question = question.strip()

        if not question:
            return question

        prompt = f"""
You are a query rewriting component for an enterprise RAG system.

Rewrite the user's question into a concise search query that improves
retrieval from a company knowledge base.

IMPORTANT RULES:

1. Preserve the exact meaning and intent of the original question.

2. NEVER change the type of question.

3. If the user asks "Who", preserve the person, role, or authority being asked for.

4. If the user asks "What database", preserve the database-related intent.

5. If the user asks for a number, price, date, version, SLA, duration,
or other specific value, preserve that exact requirement.

6. Preserve important entity names exactly, such as:
   - Project Meridian
   - Series Tech Limited
   - HR Policies v3.2

7. Do not add unrelated terms such as:
   - overview
   - description
   - purpose

   unless they are directly relevant to the original question.

8. Do not answer the question.

9. Do not invent facts.

10. Do not remove important keywords from the original question.

11. Keep the rewritten query concise.

12. Return ONLY the rewritten query.

EXAMPLES:

Original:
What is Project Meridian?

Rewritten:
Project Meridian definition overview

Original:
Who approves my leave request?

Rewritten:
Who approves leave requests reporting manager Department Head

Original:
What database does Project Meridian use?

Rewritten:
Project Meridian database MySQL

Original:
What is the maternity leave duration?

Rewritten:
Maternity leave duration

Original:
What is the exact monthly subscription price for the B2B SaaS license?

Rewritten:
B2B SaaS license exact monthly subscription price

Original:
What happens to earned leave when I resign?

Rewritten:
Earned Leave resignation encashment

USER QUESTION:
{question}

REWRITTEN QUERY:
"""

        rewritten = self.llm.generate(
            prompt
        ).strip()

        if not rewritten:
            return question

        return rewritten