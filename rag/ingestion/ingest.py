from pathlib import Path
import pickle

from rag.ingestion.loaders import load_file
from rag.ingestion.processor import split_documents

from rag.embeddings.embedding_model import get_embedding_model
from rag.vectorstore.chroma import create_vectorstore


DATA_PATH = "media"
CHUNK_PATH = "data/chunks.pkl"


def ingest():

    documents = []

    for file in Path(DATA_PATH).rglob("*"):

        if file.suffix.lower() in [".pdf", ".docx", ".txt"]:

            print(f"Loading: {file}")

            docs = load_file(str(file))

            documents.extend(docs)

    print(f"\nTotal documents: {len(documents)}")

    chunks = split_documents(documents)

    print(f"Total chunks: {len(chunks)}")

    # Save chunks for BM25
    with open(CHUNK_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("✅ Chunks saved.")

    embeddings = get_embedding_model()

    create_vectorstore(
        chunks,
        embeddings
    )

    print("✅ ChromaDB updated.")
    print("✅ Ingestion completed.")


if __name__ == "__main__":
    ingest()