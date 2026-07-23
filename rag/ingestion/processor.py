from rag.ingestion.loaders import DocumentLoader
from rag.chunking.splitter import DocumentChunker


class IngestionProcessor:
    """
    Handles document loading and chunking.

    This class is responsible only for:
    1. Loading a document
    2. Splitting it into chunks
    """

    def __init__(
        self,
        chunk_size=200,
        chunk_overlap=50
    ):

        self.loader = DocumentLoader()

        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )


    def process(
        self,
        file_path
    ):

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
        # SPLIT INTO CHUNKS
        # ==========================================

        chunks = self.chunker.split_documents(
            documents
        )


        # ==========================================
        # RETURN BOTH
        # ==========================================

        return {

            "documents": documents,

            "chunks": chunks

        }