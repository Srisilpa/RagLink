import os
import pickle
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

            docs = load_file(str(file))

            documents.extend(docs)

    print("\nTotal documents:", len(documents))

    chunks = split_documents(documents)

    print("Total chunks:", len(chunks))

    # -------------------------------------------------
    # Create data directory
    # -------------------------------------------------

    os.makedirs("data", exist_ok=True)

    # -------------------------------------------------
    # Save chunks
    # -------------------------------------------------

    with open("data/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("✅ Chunks saved.")

    # -------------------------------------------------
    # Generate embeddings
    # -------------------------------------------------

    embedding_model = get_embedding_model()

    chunk_embeddings = embedding_model.embed_documents(
        [doc.page_content for doc in chunks]
    )

    with open("data/chunk_embeddings.pkl", "wb") as f:
        pickle.dump(chunk_embeddings, f)

    print("✅ Embeddings saved.")

    # -------------------------------------------------
    # Store in ChromaDB
    # -------------------------------------------------

    create_vectorstore(
        chunks,
        embedding_model
    )

    print("✅ ChromaDB updated.")

    print("✅ Ingestion completed.")


if __name__ == "__main__":
    ingest()