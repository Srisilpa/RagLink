import json
import re

from rag.generation.llm import GroqLLM


class QueryUnderstanding:
    """
    Query understanding layer for RAGLink.

    Performs:
        1. Query rewriting
        2. Intent detection
        3. Entity extraction
        4. Metadata filter detection
    """

    def __init__(self):

        self.llm = GroqLLM()

    # =====================================================
    # MAIN METHOD
    # =====================================================

    def understand(
        self,
        question: str
    ):

        # =================================================
        # VALIDATE QUESTION
        # =================================================

        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        # =================================================
        # LLM PROMPT
        # =================================================

        prompt = f"""
You are a query analysis component for an enterprise
RAG system.

Analyze the user's question.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not explain anything.
Do not answer the question.

The JSON must have exactly these fields:

{{
    "rewritten_query": "string",
    "intent": "string",
    "entities": [],
    "metadata_filters": {{}}
}}

Allowed intents:

- technology_information
- database_information
- policy_information
- hr_information
- employee_information
- security_information
- infrastructure_information
- career_information
- payroll_information
- project_information
- general_information

Allowed metadata filter:

"document_type": "company"

OR

"document_type": "project"

Rules:

1. Preserve the meaning of the question.

2. Preserve exact project names.

3. Preserve exact company names.

4. If the question mentions "Project Meridian",
   classify it as a project query.

5. If the question asks about a database,
   intent must be "database_information".

6. If the question asks about technologies,
   intent must be "technology_information".

7. If the question asks about leave, salary,
   employee policies, or HR, classify appropriately.

8. Do not answer the question.

9. Do not invent entities.

10. Return only JSON.

Examples:

Question:
What database does Project Meridian use?

JSON:
{{
    "rewritten_query": "Project Meridian database",
    "intent": "database_information",
    "entities": ["Project Meridian"],
    "metadata_filters": {{
        "document_type": "project"
    }}
}}

Question:
What technologies are used in Project Meridian?

JSON:
{{
    "rewritten_query": "Project Meridian technology stack technologies",
    "intent": "technology_information",
    "entities": ["Project Meridian"],
    "metadata_filters": {{
        "document_type": "project"
    }}
}}

Question:
What is the maternity leave duration?

JSON:
{{
    "rewritten_query": "maternity leave duration",
    "intent": "policy_information",
    "entities": [],
    "metadata_filters": {{
        "document_type": "company"
    }}
}}

Question:
Who approves employee leave requests?

JSON:
{{
    "rewritten_query": "employee leave request approval",
    "intent": "hr_information",
    "entities": [],
    "metadata_filters": {{
        "document_type": "company"
    }}
}}

User Question:
{question}
"""

        # =================================================
        # CALL LLM
        # =================================================

        try:

            response = self.llm.generate(
                prompt
            ).strip()

        except Exception as e:

            print(
                f"Query understanding failed: {e}"
            )

            return self._fallback(
                question
            )

        # =================================================
        # PARSE LLM RESPONSE
        # =================================================

        result = self._parse_json(
            response
        )

        # =================================================
        # IF JSON PARSING FAILED
        # =================================================

        if result is None:

            print(
                "Query understanding returned invalid JSON."
            )

            return self._fallback(
                question
            )

        # =================================================
        # VALIDATE RESULT
        # =================================================

        result = self._validate_result(

            result,

            question

        )

        return result

    # =====================================================
    # JSON PARSER
    # =====================================================

    def _parse_json(
        self,
        response: str
    ):

        if not response:

            return None

        # -------------------------------------------------
        # DIRECT JSON
        # -------------------------------------------------

        try:

            return json.loads(
                response
            )

        except json.JSONDecodeError:

            pass

        # -------------------------------------------------
        # REMOVE MARKDOWN CODE BLOCK
        # -------------------------------------------------

        cleaned = re.sub(

            r"```json\s*|\s*```",

            "",

            response,

            flags=re.IGNORECASE

        ).strip()

        try:

            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:

            pass

        # -------------------------------------------------
        # EXTRACT JSON OBJECT
        # -------------------------------------------------

        match = re.search(

            r"\{.*\}",

            response,

            re.DOTALL

        )

        if match:

            try:

                return json.loads(

                    match.group(0)

                )

            except json.JSONDecodeError:

                pass

        return None

    # =====================================================
    # VALIDATE RESULT
    # =====================================================

    def _validate_result(
        self,
        result,
        question
    ):

        # -------------------------------------------------
        # REWRITTEN QUERY
        # -------------------------------------------------

        rewritten_query = result.get(

            "rewritten_query",

            question

        )

        if not isinstance(
            rewritten_query,
            str
        ):

            rewritten_query = question

        # -------------------------------------------------
        # INTENT
        # -------------------------------------------------

        intent = result.get(

            "intent",

            "general_information"

        )

        if not isinstance(
            intent,
            str
        ):

            intent = "general_information"

        # -------------------------------------------------
        # ENTITIES
        # -------------------------------------------------

        entities = result.get(

            "entities",

            []

        )

        if not isinstance(
            entities,
            list
        ):

            entities = []

        # -------------------------------------------------
        # FILTERS
        # -------------------------------------------------

        metadata_filters = result.get(

            "metadata_filters",

            {}

        )

        if not isinstance(
            metadata_filters,
            dict
        ):

            metadata_filters = {}

        # =================================================
        # SAFETY OVERRIDES
        # =================================================

        question_lower = question.lower()

        # -------------------------------------------------
        # PROJECT MERIDIAN
        # -------------------------------------------------

        if "project meridian" in question_lower:

            if "Project Meridian" not in entities:

                entities.append(
                    "Project Meridian"
                )

            metadata_filters[
                "document_type"
            ] = "project"

        # -------------------------------------------------
        # DATABASE INTENT
        # -------------------------------------------------

        if any(

            keyword in question_lower

            for keyword in [

                "database",

                "mysql",

                "postgresql",

                "postgres",

                "dynamodb",

                "sql"

            ]

        ):

            intent = (
                "database_information"
            )

        # -------------------------------------------------
        # TECHNOLOGY INTENT
        # -------------------------------------------------

        elif any(

            keyword in question_lower

            for keyword in [

                "technology",

                "technologies",

                "tech stack",

                "framework",

                "programming language"

            ]

        ):

            intent = (
                "technology_information"
            )

        # -------------------------------------------------
        # LEAVE / POLICY
        # -------------------------------------------------

        elif any(

            keyword in question_lower

            for keyword in [

                "leave",

                "maternity",

                "paternity",

                "vacation",

                "policy"

            ]

        ):

            intent = (
                "policy_information"
            )

        # -------------------------------------------------
        # HR
        # -------------------------------------------------

        elif any(

            keyword in question_lower

            for keyword in [

                "employee",

                "salary",

                "notice period",

                "resign",

                "manager",

                "department head"

            ]

        ):

            intent = (
                "hr_information"
            )

        # -------------------------------------------------
        # DEFAULT COMPANY FILTER
        # -------------------------------------------------

        if not metadata_filters:

            metadata_filters[

                "document_type"

            ] = "company"

        # =================================================
        # RETURN
        # =================================================

        return {

            "rewritten_query":
                rewritten_query.strip(),

            "intent":
                intent.strip(),

            "entities":
                entities,

            "metadata_filters":
                metadata_filters

        }

    # =====================================================
    # FALLBACK
    # =====================================================

    def _fallback(
        self,
        question: str
    ):

        question_lower = (
            question.lower()
        )

        # =================================================
        # DEFAULT VALUES
        # =================================================

        intent = (
            "general_information"
        )

        entities = []

        metadata_filters = {

            "document_type":
                "company"

        }

        rewritten_query = question

        # =================================================
        # PROJECT MERIDIAN
        # =================================================

        if "project meridian" in question_lower:

            entities.append(

                "Project Meridian"

            )

            metadata_filters[

                "document_type"

            ] = "project"

            rewritten_query = (

                "Project Meridian "

                + question_lower.replace(

                    "project meridian",

                    ""

                ).strip()

            )

        # =================================================
        # DATABASE
        # =================================================

        if "database" in question_lower:

            intent = (
                "database_information"
            )

        # =================================================
        # TECHNOLOGY
        # =================================================

        elif (

            "technology" in question_lower

            or

            "technologies" in question_lower

            or

            "tech stack" in question_lower

        ):

            intent = (
                "technology_information"
            )

        # =================================================
        # POLICY
        # =================================================

        elif (

            "leave" in question_lower

            or

            "maternity" in question_lower

            or

            "policy" in question_lower

        ):

            intent = (
                "policy_information"
            )

        # =================================================
        # RETURN
        # =================================================

        return {

            "rewritten_query":
                rewritten_query,

            "intent":
                intent,

            "entities":
                entities,

            "metadata_filters":
                metadata_filters

        }