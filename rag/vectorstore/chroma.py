import os
from langchain_chroma import Chroma


def create_vectorstore(documents, embedding_model):

    persist_directory = "chroma_db"

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory
    )

    return vectorstore