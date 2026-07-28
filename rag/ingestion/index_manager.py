import os
import pickle

from rag.embeddings.embedding_model import (
    get_embedding_model
)

from rag.retrieval.bm25 import (
    rebuild_bm25_index
)

from rag.vectorstore.chroma import (
    rebuild_vectorstore
)


CHUNKS_PATH = "data/chunks.pkl"


class IndexManager:
    """
    Central manager for RAG indexes.

    Master source of truth:

        data/chunks.pkl

    Derived indexes:

        ChromaDB
        BM25

    Architecture:

        Add Document
            ↓
        Update chunks.pkl
            ↓
        Rebuild ChromaDB
            ↓
        Rebuild BM25

        Delete Document
            ↓
        Remove chunks from chunks.pkl
            ↓
        Rebuild ChromaDB
            ↓
        Rebuild BM25
    """

    def __init__(self):

        self.embedding_model = (
            get_embedding_model()
        )

    # =====================================================
    # LOAD ALL CHUNKS
    # =====================================================

    def _load_chunks(self):

        if not os.path.exists(
            CHUNKS_PATH
        ):

            return []

        with open(
            CHUNKS_PATH,
            "rb"
        ) as f:

            chunks = pickle.load(
                f
            )

        return chunks

    # =====================================================
    # SAVE ALL CHUNKS
    # =====================================================

    def _save_chunks(
        self,
        chunks
    ):

        os.makedirs(
            "data",
            exist_ok=True
        )

        with open(
            CHUNKS_PATH,
            "wb"
        ) as f:

            pickle.dump(
                chunks,
                f
            )

    # =====================================================
    # REBUILD ALL INDEXES
    # =====================================================

    def _rebuild_indexes(
        self,
        chunks
    ):

        print(
            "\n============================================================"
        )

        print(
            "REBUILDING RAG INDEXES"
        )

        print(
            "============================================================"
        )

        print(
            f"Total chunks: {len(chunks)}"
        )

        # -------------------------------------------------
        # REBUILD CHROMADB
        # -------------------------------------------------

        print(
            "\nRebuilding ChromaDB..."
        )

        if chunks:

            rebuild_vectorstore(

                documents=chunks,

                embedding_model=(
                    self.embedding_model
                )

            )

            print(
                f"ChromaDB rebuilt with "
                f"{len(chunks)} chunks."
            )

        else:

            # Rebuild empty ChromaDB

            rebuild_vectorstore(

                documents=[],

                embedding_model=(
                    self.embedding_model
                )

            )

            print(
                "ChromaDB rebuilt empty."
            )

        # -------------------------------------------------
        # REBUILD BM25
        # -------------------------------------------------

        print(
            "\nRebuilding BM25..."
        )

        rebuild_bm25_index(
            chunks
        )

        print(
            f"BM25 rebuilt with "
            f"{len(chunks)} chunks."
        )

        print(
            "\nAll RAG indexes rebuilt successfully."
        )

    # =====================================================
    # ADD DOCUMENT
    # =====================================================

    def add_document(
        self,
        chunks
    ):

        if not chunks:

            return 0

        # -------------------------------------------------
        # GET DOCUMENT ID
        # -------------------------------------------------

        first_metadata = (

            chunks[0].metadata
            or {}

        )

        document_id = str(

            first_metadata.get(

                "document_id",

                ""

            )

        )

        if not document_id:

            raise ValueError(

                "Cannot index document: "
                "document_id missing from chunk metadata."

            )

        print(

            f"\nAdding document "
            f"{document_id} to RAG index..."

        )

        # -------------------------------------------------
        # LOAD EXISTING CHUNKS
        # -------------------------------------------------

        existing_chunks = (

            self._load_chunks()

        )

        print(

            f"Existing chunks: "
            f"{len(existing_chunks)}"

        )

        # -------------------------------------------------
        # REMOVE OLD VERSION
        # -------------------------------------------------

        filtered_chunks = [

            chunk

            for chunk in existing_chunks

            if str(

                (chunk.metadata or {}).get(

                    "document_id",

                    ""

                )

            ) != document_id

        ]

        removed_old = (

            len(existing_chunks)

            -

            len(filtered_chunks)

        )

        if removed_old:

            print(

                f"Removed {removed_old} "
                f"old chunks for document "
                f"{document_id}."

            )

        # -------------------------------------------------
        # ADD NEW CHUNKS
        # -------------------------------------------------

        filtered_chunks.extend(
            chunks
        )

        # -------------------------------------------------
        # SAVE MASTER CHUNK DATA
        # -------------------------------------------------

        self._save_chunks(

            filtered_chunks

        )

        # -------------------------------------------------
        # REBUILD INDEXES
        # -------------------------------------------------

        self._rebuild_indexes(

            filtered_chunks

        )

        print(

            f"\nIndexManager: added "
            f"{len(chunks)} chunks."

        )

        return len(chunks)

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

        # -------------------------------------------------
        # LOAD EXISTING CHUNKS
        # -------------------------------------------------

        existing_chunks = (

            self._load_chunks()

        )

        print(

            f"Current total chunks: "
            f"{len(existing_chunks)}"

        )

        # -------------------------------------------------
        # COUNT MATCHING CHUNKS
        # -------------------------------------------------

        matching_chunks = [

            chunk

            for chunk in existing_chunks

            if str(

                (chunk.metadata or {}).get(

                    "document_id",

                    ""

                )

            ) == document_id

        ]

        removed_count = len(
            matching_chunks
        )

        print(

            f"Found {removed_count} "
            f"chunks for document "
            f"{document_id}."

        )

        # -------------------------------------------------
        # REMOVE DOCUMENT CHUNKS
        # -------------------------------------------------

        remaining_chunks = [

            chunk

            for chunk in existing_chunks

            if str(

                (chunk.metadata or {}).get(

                    "document_id",

                    ""

                )

            ) != document_id

        ]

        # -------------------------------------------------
        # SAVE UPDATED MASTER DATA
        # -------------------------------------------------

        self._save_chunks(

            remaining_chunks

        )

        # -------------------------------------------------
        # REBUILD BOTH INDEXES
        # -------------------------------------------------

        self._rebuild_indexes(

            remaining_chunks

        )

        print(

            f"\nRemoved {removed_count} "
            f"chunks from RAG."

        )

        print(

            f"Remaining chunks: "
            f"{len(remaining_chunks)}"

        )

        return removed_count