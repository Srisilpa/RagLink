import os
import pickle

from rag.ingestion.processor import (
    IngestionProcessor
)

from rag.embeddings.embedding_model import (
    get_embedding_model
)

from rag.vectorstore.chroma import (
    create_vectorstore
)


# =========================================================
# CONFIGURATION
# =========================================================

MEDIA_DIR = "media"

DATA_DIR = "data"

CHUNKS_PATH = os.path.join(
    DATA_DIR,
    "chunks.pkl"
)

EMBEDDINGS_PATH = os.path.join(
    DATA_DIR,
    "chunk_embeddings.pkl"
)


# =========================================================
# GET FILES
# =========================================================

def get_files(
    directory
):

    supported_extensions = (

        ".pdf",

        ".txt",

        ".docx"

    )


    files = []


    if not os.path.exists(
        directory
    ):

        raise FileNotFoundError(

            f"Media directory not found: "
            f"{directory}"

        )


    for root, _, filenames in os.walk(
        directory
    ):

        for filename in filenames:

            if filename.lower().endswith(
                supported_extensions
            ):

                files.append(

                    os.path.join(
                        root,
                        filename
                    )

                )


    return files


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "RAGLink Ingestion Pipeline"
    )

    print(
        "=" * 60
    )


    # =====================================================
    # CREATE DATA DIRECTORY
    # =====================================================

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )


    # =====================================================
    # INITIALIZE PROCESSOR
    # =====================================================

    processor = IngestionProcessor(

        chunk_size=200,

        chunk_overlap=50

    )


    # =====================================================
    # GET FILES
    # =====================================================

    files = get_files(
        MEDIA_DIR
    )


    print(
        f"\nFound {len(files)} documents."
    )


    if not files:

        print(
            "No documents found."
        )

        return


    # =====================================================
    # STORE ALL DOCUMENTS AND CHUNKS
    # =====================================================

    all_documents = []

    all_chunks = []


    # =====================================================
    # PROCESS FILES
    # =====================================================

    for file_path in files:

        print(
            f"\nProcessing: {file_path}"
        )


        try:

            result = processor.process(
                file_path
            )


            documents = result[
                "documents"
            ]


            chunks = result[
                "chunks"
            ]


            # =============================================
            # ADD TO GLOBAL LISTS
            # =============================================

            all_documents.extend(
                documents
            )


            all_chunks.extend(
                chunks
            )


            print(
                f"Documents loaded: "
                f"{len(documents)}"
            )


            print(
                f"Chunks generated: "
                f"{len(chunks)}"
            )


            print(
                "Status: SUCCESS"
            )


        except Exception as e:

            print(
                f"Failed: {file_path}"
            )


            print(
                f"Error: {e}"
            )


    # =====================================================
    # CHECK RESULTS
    # =====================================================

    if not all_chunks:

        print(
            "\nNo chunks were generated."
        )

        return


    print(
        "\n"
        + "=" * 60
    )

    print(
        f"Total documents: "
        f"{len(all_documents)}"
    )

    print(
        f"Total chunks: "
        f"{len(all_chunks)}"
    )

    print(
        "=" * 60
    )


    # =====================================================
    # SAVE CHUNKS
    # =====================================================

    print(
        "\nSaving chunks..."
    )


    with open(
        CHUNKS_PATH,
        "wb"
    ) as f:

        pickle.dump(
            all_chunks,
            f
        )


    print(
        f"Chunks saved to: "
        f"{CHUNKS_PATH}"
    )


    # =====================================================
    # LOAD EMBEDDING MODEL
    # =====================================================

    print(
        "\nLoading embedding model..."
    )


    embedding_model = (
        get_embedding_model()
    )


    # =====================================================
    # CREATE EMBEDDINGS
    # =====================================================

    print(
        "Generating embeddings..."
    )


    texts = [

        doc.page_content

        for doc in all_chunks

    ]


    all_embeddings = (

        embedding_model
        .embed_documents(
            texts
        )

    )


    print(
        f"Generated "
        f"{len(all_embeddings)} embeddings."
    )


    # =====================================================
    # SAVE EMBEDDINGS
    # =====================================================

    with open(
        EMBEDDINGS_PATH,
        "wb"
    ) as f:

        pickle.dump(
            all_embeddings,
            f
        )


    print(
        f"Embeddings saved to: "
        f"{EMBEDDINGS_PATH}"
    )


    # =====================================================
    # CREATE CHROMADB
    # =====================================================

    print(
        "\nCreating ChromaDB..."
    )


    vectorstore = create_vectorstore(

        documents=all_chunks,

        embedding_model=embedding_model

    )


    print(
        "ChromaDB created successfully."
    )


    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "INGESTION COMPLETED SUCCESSFULLY"
    )

    print(
        "=" * 60
    )

    print(
        f"Documents: "
        f"{len(all_documents)}"
    )

    print(
        f"Chunks: "
        f"{len(all_chunks)}"
    )

    print(
        f"Chunks file: "
        f"{CHUNKS_PATH}"
    )

    print(
        f"Embeddings file: "
        f"{EMBEDDINGS_PATH}"
    )

    print(
        "ChromaDB: Created"
    )

    print(
        "=" * 60
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()