from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:
    """
    Responsible only for splitting documents into smaller chunks.
    """

    def __init__(
        self,
        chunk_size: int = 200,
        chunk_overlap: int = 50
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

    def split_documents(self, documents):
        """
        Split loaded documents into chunks.

        Args:
            documents: List of LangChain Document objects.

        Returns:
            List of chunked Document objects.
        """

        if not documents:
            return []

        return self.splitter.split_documents(
            documents
        )