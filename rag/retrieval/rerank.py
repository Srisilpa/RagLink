from typing import List, Tuple

from langchain_core.documents import Document

from sentence_transformers import CrossEncoder



class Reranker:
    """
    Cross Encoder + Entity Aware Reranker.

    Ranking signals:

    1. CrossEncoder relevance score
    2. Entity match boost
    3. Intent match boost
    """



    def __init__(
        self,
        model_name: str =
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):

        self.model_name = model_name

        self.model = CrossEncoder(
            self.model_name
        )



    # ==========================================
    # NORMALIZE ENTITIES
    # ==========================================

    def normalize_entities(
        self,
        entities
    ):

        """
        Converts:

        [
            {
              "mention":"Project Meridian",
              "canonical_name":"Project Meridian",
              "entity_type":"project"
            }
        ]

        into:

        [
            "Project Meridian"
        ]

        """


        if not entities:

            return []


        normalized = []


        for entity in entities:


            # dictionary entity

            if isinstance(
                entity,
                dict
            ):


                value = (

                    entity.get(
                        "canonical_name"
                    )

                    or

                    entity.get(
                        "mention"
                    )

                )


                if value:

                    normalized.append(
                        value
                    )



            # string entity

            elif isinstance(
                entity,
                str
            ):


                normalized.append(
                    entity
                )



        return normalized





    # ==========================================
    # RERANK
    # ==========================================


    def rerank(
        self,
        query: str,
        documents: list,
        top_k: int = 5,
        entities: List[str] = None,
        intent: str = None
    ) -> List[Tuple[Document, float]]:



        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )



        if not documents:

            return []



        # FIX ENTITY FORMAT

        entities = self.normalize_entities(
            entities
        )



        valid_documents = []

        seen = set()



        # ======================================
        # CLEAN DOCUMENTS
        # ======================================


        for item in documents:



            if isinstance(
                item,
                tuple
            ):

                document = item[0]

                retrieval_score = (

                    item[1]

                    if len(item) > 1

                    else None

                )


            else:

                document = item

                retrieval_score = None




            if not isinstance(
                document,
                Document
            ):

                continue



            if not document.page_content:

                continue



            content = (
                document.page_content
                .strip()
            )


            if not content:

                continue



            metadata = (
                document.metadata
                or {}
            )



            key = (

                metadata.get(
                    "source",
                    ""
                ),

                metadata.get(
                    "page",
                    ""
                ),

                content

            )



            if key in seen:

                continue



            seen.add(key)



            if retrieval_score is not None:

                document.metadata[
                    "retrieval_score"
                ] = float(
                    retrieval_score
                )



            valid_documents.append(
                document
            )



        if not valid_documents:

            return []





        # ======================================
        # CROSS ENCODER
        # ======================================


        pairs = []


        for doc in valid_documents:


            pairs.append(

                (
                    query,

                    doc.page_content

                )

            )



        scores = self.model.predict(
            pairs,
            show_progress_bar=False
        )



        scored_documents = []




        # ======================================
        # FINAL SCORE
        # ======================================


        for document, score in zip(

            valid_documents,

            scores

        ):


            final_score = float(
                score
            )



            content = (

                document.page_content

                .lower()

            )



            entity_bonus = 0.0



            for entity in entities:


                if entity.lower() in content:


                    entity_bonus += 0.25




            intent_bonus = 0.0



            if intent:


                if intent.lower() in content:

                    intent_bonus += 0.05




            final_score += (

                entity_bonus

                +

                intent_bonus

            )



            document.metadata[

                "rerank_score"

            ] = final_score



            document.metadata[

                "entity_bonus"

            ] = entity_bonus




            scored_documents.append(

                (

                    document,

                    final_score

                )

            )




        # ======================================
        # SORT
        # ======================================


        scored_documents.sort(

            key=lambda x:x[1],

            reverse=True

        )



        return scored_documents[:top_k]