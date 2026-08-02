"""
Enterprise Intent Classifier for RAGLink.

Uses lightweight rule-based scoring to classify
the primary intent of a user's query.
"""

from dataclasses import dataclass
from enum import Enum
import re
from typing import Dict, List


# ============================================================
# INTENT TYPES
# ============================================================

class QueryIntent(str, Enum):

    FACT = "fact"

    SUMMARY = "summary"

    COMPARISON = "comparison"

    PROCEDURE = "procedure"

    POLICY = "policy"

    DURATION = "duration"

    LIST = "list"

    DEFINITION = "definition"

    ARCHITECTURE = "architecture"

    TECH_STACK = "tech_stack"

    UNKNOWN = "unknown"


# ============================================================
# RESULT
# ============================================================

@dataclass
class IntentResult:

    intent: QueryIntent

    confidence: float


# ============================================================
# CLASSIFIER
# ============================================================

class IntentClassifier:

    def __init__(self):

        self.intent_patterns: Dict[QueryIntent, List[str]] = {

            QueryIntent.COMPARISON: [
                "compare",
                "difference",
                "differences",
                "versus",
                "vs",
                "similar",
                "similarities",
            ],

            QueryIntent.PROCEDURE: [
                "how",
                "steps",
                "procedure",
                "process",
                "apply",
                "submit",
                "configure",
                "install",
                "deploy",
                "setup",
            ],

            QueryIntent.DURATION: [
                "how long",
                "duration",
                "period",
                "days",
                "weeks",
                "months",
                "years",
            ],

            QueryIntent.POLICY: [
                "policy",
                "rule",
                "guideline",
                "regulation",
                "leave",
                "probation",
                "notice period",
            ],

            QueryIntent.TECH_STACK: [
                "database",
                "backend",
                "frontend",
                "framework",
                "technology",
                "tech stack",
                "language",
                "library",
            ],

            QueryIntent.ARCHITECTURE: [
                "architecture",
                "workflow",
                "pipeline",
                "design",
                "system",
                "component",
            ],

            QueryIntent.SUMMARY: [
                "overview",
                "summarize",
                "summary",
                "describe",
                "explain",
                "tell me about",
            ],

            QueryIntent.LIST: [
                "list",
                "show",
                "which",
                "what are",
                "all",
            ],

            QueryIntent.DEFINITION: [
                "what is",
                "define",
                "meaning",
            ],
        }

        self.priority = [

            QueryIntent.COMPARISON,

            QueryIntent.PROCEDURE,

            QueryIntent.DURATION,

            QueryIntent.POLICY,

            QueryIntent.TECH_STACK,

            QueryIntent.ARCHITECTURE,

            QueryIntent.SUMMARY,

            QueryIntent.LIST,

            QueryIntent.DEFINITION,

            QueryIntent.FACT,

        ]

    # ========================================================
    # NORMALIZE
    # ========================================================

    def _normalize(
        self,
        text: str,
    ) -> str:

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ========================================================
    # CLASSIFY
    # ========================================================

    def classify(
        self,
        question: str,
    ) -> IntentResult:

        if not question:

            return IntentResult(

                QueryIntent.UNKNOWN,

                0.0,

            )

        text = self._normalize(question)

        scores = {}

        for intent, keywords in self.intent_patterns.items():

            score = 0

            for keyword in keywords:

                if keyword in text:

                    if " " in keyword:
                        score += 2
                    else:
                        score += 1

            scores[intent] = score

        best_score = max(scores.values(), default=0)

        if best_score == 0:

            return IntentResult(

                QueryIntent.FACT,

                0.50,

            )

        candidates = [

            intent

            for intent, score in scores.items()

            if score == best_score

        ]

        for intent in self.priority:

            if intent in candidates:

                best_intent = intent
                break

        confidence = min(

            0.95,

            0.55 + (best_score * 0.10),

        )

        return IntentResult(

            intent=best_intent,

            confidence=round(confidence, 2),

        )