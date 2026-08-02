"""
Enterprise Query Expander for RAGLink.

The expander creates additional retrieval queries
based on the detected intent.

The original rewritten query is always preserved.
Expansion is conservative to improve recall without
adding excessive retrieval noise.
"""

from typing import Dict
from typing import List

from rag.query_understanding.intent_classifier import QueryIntent


class QueryExpander:
    """
    Intent-aware query expansion.
    """

    MAX_EXPANSIONS = 6

    def __init__(self):

        self.intent_terms: Dict[QueryIntent, List[str]] = {

            QueryIntent.DURATION: [

                "duration",

                "leave policy",

                "leave entitlement",

                "eligibility",

                "validity",

            ],

            QueryIntent.PROCEDURE: [

                "procedure",

                "process",

                "workflow",

                "steps",

                "approval",

            ],

            QueryIntent.POLICY: [

                "policy",

                "guidelines",

                "rules",

                "eligibility",

                "conditions",

            ],

            QueryIntent.TECH_STACK: [

                "technology stack",

                "architecture",

                "framework",

                "database",

                "deployment",

            ],

            QueryIntent.ARCHITECTURE: [

                "architecture",

                "components",

                "system design",

                "workflow",

                "design pattern",

            ],

            QueryIntent.COMPARISON: [

                "comparison",

                "differences",

                "similarities",

            ],

            QueryIntent.SUMMARY: [

                "overview",

                "summary",

                "details",

            ],

            QueryIntent.DEFINITION: [

                "definition",

                "overview",

                "description",

            ],

        }

    # =========================================================
    # EXPAND QUERY
    # =========================================================

    def expand(

        self,

        rewritten_query: str,

        intent: QueryIntent,

    ) -> List[str]:

        if not rewritten_query:

            return []

        rewritten_query = rewritten_query.strip()

        expansions = [rewritten_query]

        keywords = self.intent_terms.get(intent, [])

        base = rewritten_query.lower()

        for keyword in keywords:

            # Skip duplicate concepts already
            # present in the rewritten query.
            if keyword.lower() in base:

                continue

            candidate = f"{rewritten_query} {keyword}"

            if candidate not in expansions:

                expansions.append(candidate)

            if len(expansions) >= self.MAX_EXPANSIONS:

                break

        return expansions