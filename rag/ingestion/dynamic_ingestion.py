import os

from rag.ingestion.document_indexer import (
    index_document,
    delete_document_from_index
)


class DynamicIngestionManager:
    """
    Handles dynamic document ingestion and deletion.

    Django Document ID is used as the permanent
    RAG document identifier.

    Master data:

        data/chunks.pkl

    Rebuilt indexes:

        ChromaDB
        BM25
        Embeddings
    """

    # =====================================================
    # INGEST DOCUMENT
    # =====================================================

    def ingest_document(
        self,
        file_path,
        document_id,
        document_type=None
    ):

        if not file_path:

            raise ValueError(

                "File path cannot be empty."

            )

        if not os.path.exists(
            file_path
        ):

            raise FileNotFoundError(

                file_path

            )

        document_id = str(
            document_id
        )

        print(

            "\n============================================================"

        )

        print(

            "DYNAMIC DOCUMENT INGESTION"

        )

        print(

            "============================================================"

        )

        print(

            f"Document ID: {document_id}"

        )

        print(

            f"File: {file_path}"

        )

        # =================================================
        # INDEX DOCUMENT
        # =================================================

        index_document(

            file_path=file_path,

            document_id=document_id

        )

        # =================================================
        # GET ACTUAL CHUNK COUNT
        # =================================================

        from rag.ingestion.document_indexer import (
            load_all_chunks
        )

        all_chunks = load_all_chunks()

        chunk_count = sum(

            1

            for chunk in all_chunks

            if str(

                (chunk.metadata or {}).get(

                    "document_id",

                    ""

                )

            ) == document_id

        )

        print(

            "\n============================================================"

        )

        print(

            "DYNAMIC DOCUMENT INGESTION COMPLETED"

        )

        print(

            "============================================================"

        )

        print(

            f"Document ID: {document_id}"

        )

        print(

            f"Generated chunks: {chunk_count}"

        )

        return {

            "document_id":
                document_id,

            "chunks":
                chunk_count,

            "status":
                "success"

        }

    # =====================================================
    # DELETE DOCUMENT
    # =====================================================

    def delete_document(
        self,
        document_id
    ):

        document_id = str(

            document_id

        )

        print(

            "\n============================================================"

        )

        print(

            "DYNAMIC DOCUMENT DELETION"

        )

        print(

            "============================================================"

        )

        print(

            f"Document ID: {document_id}"

        )

        # =================================================
        # DELETE FROM MASTER DATA
        # =================================================

        from rag.ingestion.document_indexer import (
            load_all_chunks
        )

        existing_chunks = load_all_chunks()

        old_count = len(

            existing_chunks

        )

        # =================================================
        # COUNT DOCUMENT CHUNKS
        # =================================================

        removed_count = sum(

            1

            for chunk in existing_chunks

            if str(

                (chunk.metadata or {}).get(

                    "document_id",

                    ""

                )

            ) == document_id

        )

        # =================================================
        # DELETE + REBUILD ALL INDEXES
        # =================================================

        delete_document_from_index(

            document_id

        )

        # =================================================
        # VERIFY
        # =================================================

        remaining_chunks = load_all_chunks()

        new_count = len(

            remaining_chunks

        )

        print(

            "\n============================================================"

        )

        print(

            "DYNAMIC DOCUMENT DELETION COMPLETED"

        )

        print(

            "============================================================"

        )

        print(

            f"Document ID: {document_id}"

        )

        print(

            f"Old total chunks: {old_count}"

        )

        print(

            f"Removed chunks: {removed_count}"

        )

        print(

            f"New total chunks: {new_count}"

        )

        print(

            "ChromaDB rebuilt."

        )

        print(

            "BM25 index rebuilt."

        )

        print(

            "Embeddings rebuilt."

        )

        print(

            "============================================================"

        )

        return {

            "document_id":
                document_id,

            "removed_chunks":
                removed_count,

            "status":
                "success"

        }