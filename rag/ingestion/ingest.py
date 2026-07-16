from pathlib import Path

from rag.ingestion.loaders import load_file
from rag.ingestion.processor import split_documents

from rag.embeddings.embedding_model import get_embedding_model
from rag.vectorstore.chroma import create_vectorstore


DATA_PATH = "media"


def ingest():

    documents = []


    for file in Path(DATA_PATH).rglob("*"):

        if file.suffix.lower() in [
            ".pdf",
            ".docx",
            ".txt"
        ]:

            print("Loading:", file)


            docs = load_file(
                str(file)
            )


            documents.extend(docs)



    print("\nTotal documents:", len(documents))


    chunks = split_documents(
        documents
    )


    print("Total chunks:", len(chunks))


    embeddings = get_embedding_model()


    create_vectorstore(
        chunks,
        embeddings
    )


    print("✅ Ingestion completed")


if __name__ == "__main__":
    ingest()