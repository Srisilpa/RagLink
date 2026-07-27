import re

from typing import List, Tuple

from langchain_core.documents import Document


class ContextRefiner:
    """
    Refines reranked documents before sending them
    to the LLM.

    Pipeline:

        Reranked Documents
                ↓
        Sentence Extraction
                ↓
        Keyword Relevance
                ↓
        Relevant Sentences
                ↓
        Clean Context

    The goal is to reduce irrelevant information
    while preserving the most relevant content.
    """

    def __init__(
        self,
        max_sentences_per_document: int = 5,
        min_keyword_overlap: int = 1,
        max_context_chars: int = 8000
    ):

        self.max_sentences_per_document = (
            max_sentences_per_document
        )

        self.min_keyword_overlap = (
            min_keyword_overlap
        )

        self.max_context_chars = (
            max_context_chars
        )

    # ==========================================
    # MAIN REFINE METHOD
    # ==========================================

    def refine(
        self,
        query: str,
        documents: List
    ) -> str:
        """
        Refine reranked documents into
        a concise context string.

        Parameters:

            query:
                User query or rewritten query.

            documents:
                Reranked documents.

        Returns:

            Clean context string.
        """

        # ======================================
        # VALIDATE QUERY
        # ======================================

        if not query or not query.strip():

            return ""

        # ======================================
        # VALIDATE DOCUMENTS
        # ======================================

        if not documents:

            return ""

        # ======================================
        # EXTRACT QUERY KEYWORDS
        # ======================================

        query_keywords = self._extract_keywords(
            query
        )

        if not query_keywords:

            return self._fallback_context(
                documents
            )

        # ======================================
        # PROCESS DOCUMENTS
        # ======================================

        refined_sections = []

        for rank, item in enumerate(
            documents,
            start=1
        ):

            # ----------------------------------
            # SUPPORT:
            #
            # Document
            #
            # OR
            #
            # (Document, score)
            # ----------------------------------

            if isinstance(
                item,
                tuple
            ):

                document = item[0]

                score = item[1]

            else:

                document = item

                score = None

            # ----------------------------------
            # VALIDATE DOCUMENT
            # ----------------------------------

            if not isinstance(
                document,
                Document
            ):

                continue

            if not document.page_content:

                continue

            # ----------------------------------
            # EXTRACT SENTENCES
            # ----------------------------------

            sentences = self._split_sentences(

                document.page_content

            )

            # ----------------------------------
            # SCORE SENTENCES
            # ----------------------------------

            scored_sentences = []

            for sentence in sentences:

                sentence_keywords = (

                    self._extract_keywords(
                        sentence
                    )

                )

                overlap = (

                    query_keywords
                    &
                    sentence_keywords

                )

                relevance_score = len(
                    overlap
                )

                if relevance_score >= (
                    self.min_keyword_overlap
                ):

                    scored_sentences.append(

                        (
                            sentence,

                            relevance_score

                        )

                    )

            # ----------------------------------
            # SORT SENTENCES
            # ----------------------------------

            scored_sentences.sort(

                key=lambda item: item[1],

                reverse=True

            )

            # ----------------------------------
            # SELECT TOP SENTENCES
            # ----------------------------------

            selected_sentences = [

                sentence

                for sentence, _

                in scored_sentences[
                    :self.max_sentences_per_document
                ]

            ]

            # ----------------------------------
            # FALLBACK
            # ----------------------------------

            if not selected_sentences:

                selected_sentences = (

                    sentences[
                        :self.max_sentences_per_document
                    ]

                )

            # ----------------------------------
            # CREATE DOCUMENT SECTION
            # ----------------------------------

            if selected_sentences:

                source = (

                    document.metadata.get(
                        "file_name",
                        "Unknown document"
                    )

                )

                section = (

                    f"[Document {rank} | "
                    f"Source: {source}]\n"

                    +

                    " ".join(
                        selected_sentences
                    )

                )

                refined_sections.append(

                    section

                )

        # ======================================
        # NO REFINED CONTENT
        # ======================================

        if not refined_sections:

            return ""

        # ======================================
        # COMBINE CONTEXT
        # ======================================

        context = "\n\n".join(

            refined_sections

        )

        # ======================================
        # LIMIT CONTEXT SIZE
        # ======================================

        if len(context) > self.max_context_chars:

            context = (

                context[
                    :self.max_context_chars
                ]

            )

        return context

    # ==========================================
    # EXTRACT KEYWORDS
    # ==========================================

    def _extract_keywords(
        self,
        text: str
    ) -> set:
        """
        Extract meaningful lowercase keywords.

        Removes common stopwords.
        """

        if not text:

            return set()

        # --------------------------------------
        # NORMALIZE TEXT
        # --------------------------------------

        text = text.lower()

        # --------------------------------------
        # TOKENIZE
        # --------------------------------------

        words = re.findall(

            r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",

            text

        )

        # --------------------------------------
        # STOPWORDS
        # --------------------------------------

        stopwords = {

            "the",
            "is",
            "are",
            "was",
            "were",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "from",
            "with",
            "by",
            "about",
            "what",
            "which",
            "who",
            "when",
            "where",
            "why",
            "how",
            "does",
            "do",
            "did",
            "use",
            "used",
            "using",
            "can",
            "could",
            "would",
            "should",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
            "they",
            "their"

        }

        # --------------------------------------
        # FILTER KEYWORDS
        # --------------------------------------

        keywords = {

            word

            for word in words

            if word not in stopwords

            and len(word) > 2

        }

        return keywords

    # ==========================================
    # SPLIT INTO SENTENCES
    # ==========================================

    def _split_sentences(
        self,
        text: str
    ) -> List[str]:
        """
        Split document text into sentences.
        """

        if not text:

            return []

        # --------------------------------------
        # NORMALIZE WHITESPACE
        # --------------------------------------

        text = re.sub(

            r"\s+",

            " ",

            text

        ).strip()

        # --------------------------------------
        # SPLIT SENTENCES
        # --------------------------------------

        sentences = re.split(

            r"(?<=[.!?])\s+",

            text

        )

        # --------------------------------------
        # CLEAN SENTENCES
        # --------------------------------------

        cleaned = [

            sentence.strip()

            for sentence in sentences

            if sentence.strip()

        ]

        return cleaned

    # ==========================================
    # FALLBACK CONTEXT
    # ==========================================

    def _fallback_context(
        self,
        documents: List
    ) -> str:
        """
        Fallback when query keywords cannot
        be extracted.
        """

        sections = []

        for rank, item in enumerate(

            documents,

            start=1

        ):

            if isinstance(
                item,
                tuple
            ):

                document = item[0]

            else:

                document = item

            if not isinstance(
                document,
                Document
            ):

                continue

            if not document.page_content:

                continue

            source = (

                document.metadata.get(

                    "file_name",

                    "Unknown document"

                )

            )

            sections.append(

                f"[Document {rank} | "
                f"Source: {source}]\n"
                f"{document.page_content.strip()}"

            )

        context = "\n\n".join(

            sections

        )

        return context[
            :self.max_context_chars
        ]