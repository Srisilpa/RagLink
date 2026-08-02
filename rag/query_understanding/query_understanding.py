import json
import re
from typing import Dict, Any

from rag.generation.llm import GroqLLM

from rag.query_understanding.intent_classifier import (
    IntentClassifier,
)

from rag.query_understanding.query_expander import (
    QueryExpander,
)

from rag.query_understanding.entity_normalizer import (
    normalise_entities,
)


class QueryUnderstanding:
    """
    Enterprise Query Understanding Pipeline.

    Steps
    -----
    1. Query rewriting
    2. Intent classification
    3. Entity extraction
    4. Entity normalization
    5. Query expansion
    6. Metadata filter generation
    """

    def __init__(self):

        self.llm = GroqLLM()

        self.intent_classifier = (
            IntentClassifier()
        )

        self.query_expander = (
            QueryExpander()
        )

    # ======================================================
    # MAIN PIPELINE
    # ======================================================

    def understand(
        self,
        question: str,
    ) -> Dict[str, Any]:

        if not question:

            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        if not question:

            raise ValueError(
                "Question cannot be empty."
            )

        # ------------------------------------------
        # LLM Analysis
        # ------------------------------------------

        llm_result = self._analyse_with_llm(
            question
        )

        rewritten_query = llm_result.get(
            "rewritten_query",
            question,
        )

        extracted_entities = llm_result.get(
            "entities",
            [],
        )

        metadata_filters = llm_result.get(
            "metadata_filters",
            {},
        )

        # ------------------------------------------
        # Intent Classification
        # ------------------------------------------

        intent_result = (
            self.intent_classifier.classify(
                rewritten_query
            )
        )

        # ------------------------------------------
        # Entity Normalization
        # ------------------------------------------

        entities = normalise_entities(
            extracted_entities
        )

        # ------------------------------------------
        # Query Expansion
        # ------------------------------------------

        expanded_queries = (
            self.query_expander.expand(
                rewritten_query,
                intent_result.intent,
            )
        )

        # ------------------------------------------
        # Metadata Filters
        # ------------------------------------------

        metadata_filters = (
            self._build_metadata_filters(
                entities,
                metadata_filters,
            )
        )


                # ------------------------------------------
        # Validate
        # ------------------------------------------

        result = self._validate_result(

            {

                "rewritten_query":
                    rewritten_query,

                "intent":
                    intent_result.intent.value,

                "entities":
                    entities,

                "metadata_filters":
                    metadata_filters,

            },

            question,

        )

        result["expanded_queries"] = (
            expanded_queries
        )

        return result

    # ======================================================
    # LLM ANALYSIS
    # ======================================================

    def _analyse_with_llm(
        self,
        question: str,
    ) -> Dict[str, Any]:

        prompt = self._build_prompt(
            question
        )

        try:

            response = self.llm.generate(
                prompt
            ).strip()

            parsed = self._parse_json(
                response
            )

            if parsed:

                return parsed

        except Exception as e:

            print(
                f"Query understanding failed: {e}"
            )

        return self._fallback(
            question
        )


        # ======================================================
    # BUILD PROMPT
    # ======================================================

    def _build_prompt(
        self,
        question: str,
    ) -> str:

        return f"""
You are an Enterprise Query Understanding Engine inside a Retrieval-Augmented Generation (RAG) system.

Your job is ONLY to understand the user's query.

DO NOT answer the question.

Return ONLY valid JSON.

Return exactly this schema:

{{
    "rewritten_query": "",
    "entities": [],
    "metadata_filters": {{}}
}}

RULES

1. Rewrite the query into a concise enterprise search query.

2. Preserve all project names exactly.

3. Preserve all company names exactly.

4. Preserve cloud providers exactly.

5. Preserve databases exactly.

6. Never invent entities.

7. Never invent metadata filters.

8. If no entities exist return [].

9. If no metadata filters exist return {{}}.

10. Return JSON only.

--------------------------------

Examples

Question:
Tell me about Meridian.

Output:

{{
    "rewritten_query":"Project Meridian overview",
    "entities":["Project Meridian"],
    "metadata_filters":{{}}
}}

Question:
Explain AWS infrastructure.

Output:

{{
    "rewritten_query":"AWS cloud infrastructure",
    "entities":["AWS"],
    "metadata_filters":{{}}
}}

Question:
What database does Project Meridian use?

Output:

{{
    "rewritten_query":"Project Meridian database",
    "entities":["Project Meridian"],
    "metadata_filters":{{}}
}}

Question:
Explain Azure storage.

Output:

{{
    "rewritten_query":"Azure storage architecture",
    "entities":["Azure"],
    "metadata_filters":{{}}
}}

--------------------------------

USER QUESTION

{question}
"""

    # ======================================================
    # PARSE JSON
    # ======================================================

    def _parse_json(
        self,
        response: str,
    ) -> Dict[str, Any] | None:

        if not response:

            return None

        # ------------------------------------------
        # Direct JSON
        # ------------------------------------------

        try:

            return json.loads(response)

        except Exception:

            pass

        # ------------------------------------------
        # Remove Markdown
        # ------------------------------------------

        cleaned = re.sub(
            r"```json|```",
            "",
            response,
            flags=re.IGNORECASE,
        ).strip()

        try:

            return json.loads(cleaned)

        except Exception:

            pass

        # ------------------------------------------
        # Extract JSON Object
        # ------------------------------------------

        match = re.search(
            r"\{[\s\S]*\}",
            cleaned,
        )

        if match:

            try:

                return json.loads(
                    match.group()
                )

            except Exception:

                pass

        print(
            "Invalid JSON returned from Query Understanding LLM."
        )

        return None


        # ======================================================
    # FALLBACK
    # ======================================================

    def _fallback(
        self,
        question: str,
    ) -> Dict[str, Any]:

        rewritten_query = question.strip()

        intent_result = self.intent_classifier.classify(
            rewritten_query
        )

        extracted_entities = []

        question_lower = question.lower()

        if "meridian" in question_lower:
            extracted_entities.append("Project Meridian")

        if (
            "series tech" in question_lower
            or "series tech limited" in question_lower
        ):
            extracted_entities.append(
                "Series Tech Limited"
            )

        if (
            "aws" in question_lower
            or "amazon web services" in question_lower
        ):
            extracted_entities.append("AWS")

        if "azure" in question_lower:
            extracted_entities.append("Azure")

        entities = normalise_entities(
            extracted_entities
        )

        metadata_filters = (
            self._build_metadata_filters(
                entities,
                {},
            )
        )

        expanded_queries = (
            self.query_expander.expand(
                rewritten_query,
                intent_result.intent,
            )
        )

        return {

            "rewritten_query":
                rewritten_query,

            "intent":
                intent_result.intent.value,

            "entities":
                entities,

            "metadata_filters":
                metadata_filters,

            "expanded_queries":
                expanded_queries,

        }

    # ======================================================
    # VALIDATE RESULT
    # ======================================================

    def _validate_result(
        self,
        result: Dict[str, Any],
        question: str,
    ) -> Dict[str, Any]:

        rewritten_query = result.get(
            "rewritten_query",
            question,
        )

        if (
            not isinstance(
                rewritten_query,
                str,
            )
            or
            not rewritten_query.strip()
        ):

            rewritten_query = question

        intent = result.get(
            "intent",
            "fact",
        )

        if not isinstance(
            intent,
            str,
        ):
            intent = "fact"

        entities = result.get(
            "entities",
            [],
        )

        if not isinstance(
            entities,
            list,
        ):
            entities = []

        metadata_filters = result.get(
            "metadata_filters",
            {},
        )

        if not isinstance(
            metadata_filters,
            dict,
        ):
            metadata_filters = {}

        # ------------------------------------------
        # Remove duplicate entities
        # ------------------------------------------

        unique_entities = []

        seen = set()

        for entity in entities:

            if not isinstance(
                entity,
                dict,
            ):
                continue

            key = (

                entity.get(
                    "canonical_name"
                ),

                entity.get(
                    "entity_type"
                ),

            )

            if key in seen:
                continue

            seen.add(key)

            unique_entities.append(
                entity
            )

        return {

            "rewritten_query":
                rewritten_query.strip(),

            "intent":
                intent,

            "entities":
                unique_entities,

            "metadata_filters":
                metadata_filters,

        }



        # ======================================================
    # BUILD METADATA FILTERS
    # ======================================================

    def _build_metadata_filters(
        self,
        entities,
        existing_filters,
    ):
        """
        Build metadata filters from normalized entities.

        Normalized entities look like:

        {
            "mention": "Meridian",
            "canonical_name": "Project Meridian",
            "entity_type": "project"
        }
        """

        filters = dict(existing_filters)

        if not isinstance(entities, list):
            return filters

        document_types = set()

        project_names = []
        company_names = []
        technologies = []

        for entity in entities:

            if not isinstance(entity, dict):
                continue

            canonical_name = entity.get(
                "canonical_name",
                "",
            )

            entity_type = entity.get(
                "entity_type",
                "",
            )

            # -------------------------------
            # Document Type
            # -------------------------------

            if entity_type == "project":

                document_types.add(
                    "project"
                )

                project_names.append(
                    canonical_name
                )

            elif entity_type == "company":

                document_types.add(
                    "company"
                )

                company_names.append(
                    canonical_name
                )

            elif entity_type == "infrastructure":

                document_types.add(
                    "infrastructure"
                )

                technologies.append(
                    canonical_name
                )

        # ----------------------------------
        # Store filters
        # ----------------------------------

        if document_types:

            filters["document_types"] = sorted(
                list(document_types)
            )

        if project_names:

            filters["projects"] = sorted(
                list(set(project_names))
            )

        if company_names:

            filters["companies"] = sorted(
                list(set(company_names))
            )

        if technologies:

            filters["technologies"] = sorted(
                list(set(technologies))
            )

        return filters