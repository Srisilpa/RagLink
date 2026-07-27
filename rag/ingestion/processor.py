from rag.ingestion.loaders import (
    DocumentLoader
)

from rag.chunking.splitter import (
    DocumentSplitter
)


class IngestionProcessor:
    """
    Handles document loading, chunking and
    metadata enrichment.

    Responsibilities:

    1. Load documents
    2. Split documents into chunks
    3. Add chunk-level metadata
    """

    def __init__(
        self,
        chunk_size=200,
        chunk_overlap=50
    ):

        self.loader = DocumentLoader()

        self.chunker = DocumentSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    # ==========================================
    # PROCESS DOCUMENT
    # ==========================================

    def process(
        self,
        file_path
    ):

        # ==========================================
        # VALIDATE FILE PATH
        # ==========================================

        if not file_path:

            raise ValueError(
                "File path cannot be empty."
            )

        # ==========================================
        # LOAD DOCUMENT
        # ==========================================

        documents = self.loader.load(
            file_path
        )

        # ==========================================
        # SPLIT DOCUMENTS
        # ==========================================

        chunks = self.chunker.split_documents(
            documents
        )

        # ==========================================
        # ADD CHUNK METADATA
        # ==========================================

        for index, chunk in enumerate(
            chunks
        ):

            # --------------------------------------
            # MAKE SURE METADATA EXISTS
            # --------------------------------------

            if chunk.metadata is None:

                chunk.metadata = {}

            # --------------------------------------
            # GET FILE NAME
            # --------------------------------------

            file_name = chunk.metadata.get(
                "file_name",
                "document"
            )

            # --------------------------------------
            # CREATE UNIQUE CHUNK ID
            # --------------------------------------

            chunk.metadata[
                "chunk_id"
            ] = (
                f"{file_name}_{index}"
            )

            # --------------------------------------
            # CHUNK INDEX
            # --------------------------------------

            chunk.metadata[
                "chunk_index"
            ] = index

            # --------------------------------------
            # TOTAL CHUNKS
            # --------------------------------------

            chunk.metadata[
                "total_chunks"
            ] = len(
                chunks
            )

        # ==========================================
        # RETURN RESULT
        # ==========================================

        return {

            "documents": documents,

            "chunks": chunks

        }