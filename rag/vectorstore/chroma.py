import os

from langchain_chroma import Chroma


CHROMA_PATH = "chroma_db"


def create_vectorstore(documents, embedding_model):
    """
    Create and persist a Chroma vector database.
    """

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=CHROMA_PATH,
    )

    return vectorstore


def load_vectorstore(embedding_model):
    """
    Load an existing Chroma vector database.
    """

    if not os.path.exists(CHROMA_PATH):
        raise FileNotFoundError(
            f"Vector database not found: {CHROMA_PATH}"
        )

    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model,
    )