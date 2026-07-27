import os

from langchain_chroma import Chroma


CHROMA_PATH = "chroma_db"


def create_vectorstore(
    documents,
    embedding_model
):

    vectorstore = Chroma.from_documents(

        documents=documents,

        embedding=embedding_model,

        persist_directory=CHROMA_PATH,

    )

    return vectorstore


def load_vectorstore(
    embedding_model
):

    if not os.path.exists(
        CHROMA_PATH
    ):

        raise FileNotFoundError(

            f"Vector database not found: "
            f"{CHROMA_PATH}"

        )

    return Chroma(

        persist_directory=CHROMA_PATH,

        embedding_function=embedding_model,

    )