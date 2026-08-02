import os

from langchain_chroma import Chroma


# =========================================================
# CONFIGURATION
# =========================================================

CHROMA_PATH = "chroma_db"


# =========================================================
# CREATE VECTORSTORE
# =========================================================

def create_vectorstore(
    documents,
    embedding_model
):
    """
    Create a new ChromaDB vectorstore.

    This should mainly be used when creating
    the vector database for the first time.
    """

    if not documents:

        print(
            "No documents available to create ChromaDB."
        )

        return None

    os.makedirs(
        CHROMA_PATH,
        exist_ok=True
    )

    vectorstore = Chroma.from_documents(

        documents=documents,

        embedding=embedding_model,

        persist_directory=CHROMA_PATH,

    )

    print(
        f"ChromaDB created with "
        f"{len(documents)} chunks."
    )

    return vectorstore


# =========================================================
# LOAD VECTORSTORE
# =========================================================

def load_vectorstore(
    embedding_model
):
    """
    Load the existing ChromaDB vectorstore.

    Raises FileNotFoundError if ChromaDB
    does not exist yet.
    """

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


# =========================================================
# ADD DOCUMENT TO CHROMA
# =========================================================

def add_documents_to_chroma(
    documents,
    embedding_model
):
    """
    Add new document chunks to the existing
    ChromaDB vectorstore.

    This performs an incremental update.

    It does NOT delete or rebuild the
    entire ChromaDB database.
    """

    if not documents:

        print(
            "No documents to add to ChromaDB."
        )

        return 0

    # -----------------------------------------------------
    # CREATE DATABASE IF IT DOES NOT EXIST
    # -----------------------------------------------------

    if not os.path.exists(
        CHROMA_PATH
    ):

        print(
            "ChromaDB does not exist."
        )

        print(
            "Creating new ChromaDB..."
        )

        create_vectorstore(

            documents,

            embedding_model

        )

        return len(
            documents
        )

    # -----------------------------------------------------
    # LOAD EXISTING DATABASE
    # -----------------------------------------------------

    vectorstore = load_vectorstore(

        embedding_model

    )

    # -----------------------------------------------------
    # ADD ONLY NEW CHUNKS
    # -----------------------------------------------------

    vectorstore.add_documents(

        documents

    )

    print(

        f"ChromaDB: added "
        f"{len(documents)} new chunks."

    )

    return len(
        documents
    )


# =========================================================
# DELETE DOCUMENT FROM CHROMA
# =========================================================

def delete_document_from_chroma(
    document_id,
    embedding_model
):
    """
    Delete all chunks belonging to a Django
    document from ChromaDB.

    Only the matching chunks are deleted.

    The entire ChromaDB database is preserved.
    """

    document_id = str(
        document_id
    )

    # -----------------------------------------------------
    # CHECK CHROMA DATABASE
    # -----------------------------------------------------

    if not os.path.exists(
        CHROMA_PATH
    ):

        print(

            f"ChromaDB not found. "
            f"Nothing to delete for "
            f"document {document_id}."

        )

        return 0

    # -----------------------------------------------------
    # LOAD VECTORSTORE
    # -----------------------------------------------------

    vectorstore = load_vectorstore(

        embedding_model

    )

    # -----------------------------------------------------
    # FIND MATCHING CHUNKS
    # -----------------------------------------------------

    result = vectorstore.get(

        where={

            "document_id":
                document_id

        }

    )

    ids = result.get(

        "ids",

        []

    )

    # -----------------------------------------------------
    # NO MATCHING CHUNKS
    # -----------------------------------------------------

    if not ids:

        print(

            f"No Chroma chunks found "
            f"for document {document_id}."

        )

        return 0

    # -----------------------------------------------------
    # DELETE ONLY MATCHING CHUNKS
    # -----------------------------------------------------

    vectorstore.delete(

        ids=ids

    )

    print(

        f"ChromaDB: removed "
        f"{len(ids)} chunks for "
        f"document {document_id}."

    )

    return len(
        ids
    )


# =========================================================
# UPDATE DOCUMENT IN CHROMA
# =========================================================

def update_document_in_chroma(
    document_id,
    documents,
    embedding_model
):
    """
    Update an existing document in ChromaDB.

    Process:

        1. Delete old chunks
        2. Add new chunks

    The entire ChromaDB database is NOT rebuilt.
    """

    document_id = str(
        document_id
    )

    print(

        f"\nUpdating ChromaDB document "
        f"{document_id}..."

    )

    # -----------------------------------------------------
    # DELETE OLD CHUNKS
    # -----------------------------------------------------

    removed_count = (

        delete_document_from_chroma(

            document_id,

            embedding_model

        )

    )

    # -----------------------------------------------------
    # ADD NEW CHUNKS
    # -----------------------------------------------------

    added_count = 0

    if documents:

        added_count = (

            add_documents_to_chroma(

                documents,

                embedding_model

            )

        )

    print(

        f"ChromaDB update completed. "

        f"Removed: {removed_count}, "

        f"Added: {added_count}."

    )

    return {

        "removed": removed_count,

        "added": added_count

    }


# =========================================================
# GET DOCUMENT CHUNK COUNT
# =========================================================

def get_document_chunk_count(
    document_id,
    embedding_model
):
    """
    Return the number of chunks stored in
    ChromaDB for a specific document.
    """

    document_id = str(
        document_id
    )

    if not os.path.exists(
        CHROMA_PATH
    ):

        return 0

    vectorstore = load_vectorstore(

        embedding_model

    )

    result = vectorstore.get(

        where={

            "document_id":
                document_id

        }

    )

    ids = result.get(

        "ids",

        []

    )

    return len(
        ids
    )


# =========================================================
# CHECK CHROMA DATABASE
# =========================================================

def chroma_exists():

    return os.path.exists(

        CHROMA_PATH

    )


# =========================================================
# REBUILD VECTORSTORE
# =========================================================

def rebuild_vectorstore(
    documents,
    embedding_model
):
    """
    Completely rebuild ChromaDB.

    WARNING:

    This function deletes the existing ChromaDB
    directory.

    Use this only for:

        - Initial setup
        - Manual full rebuild
        - Recovery

    Do NOT call this after every document upload
    or deletion.

    Incremental operations should use:

        add_documents_to_chroma()

        delete_document_from_chroma()

        update_document_in_chroma()
    """

    print(

        "\nRebuilding ChromaDB..."

    )

    # -----------------------------------------------------
    # IMPORTANT
    # -----------------------------------------------------
    #
    # We intentionally do NOT delete the existing
    # ChromaDB directory here automatically.
    #
    # The existing database should be cleared manually
    # only when a full rebuild is explicitly required.
    #
    # This prevents Windows file-lock errors caused by
    # deleting ChromaDB while another process has it open.
    #
    # -----------------------------------------------------

    if not documents:

        print(

            "No documents available."

        )

        return None

    # -----------------------------------------------------
    # IF DATABASE DOES NOT EXIST
    # -----------------------------------------------------

    if not os.path.exists(
        CHROMA_PATH
    ):

        vectorstore = Chroma.from_documents(

            documents=documents,

            embedding=embedding_model,

            persist_directory=CHROMA_PATH,

        )

        print(

            f"ChromaDB created with "
            f"{len(documents)} chunks."

        )

        return vectorstore

    # -----------------------------------------------------
    # EXISTING DATABASE
    # -----------------------------------------------------

    print(

        "Existing ChromaDB detected."

    )

    print(

        "Use incremental indexing instead of "
        "rebuilding the database."

    )

    return load_vectorstore(

        embedding_model

    )


# =========================================================
# GET VECTORSTORE (UTILITY FUNCTION)
# =========================================================

def get_vectorstore():
    """
    Load existing ChromaDB vectorstore.

    Used by:
    - metadata checking scripts
    - testing utilities
    """

    from rag.embeddings.embedding_model import (
        get_embedding_model
    )

    embedding_model = get_embedding_model()

    return load_vectorstore(
        embedding_model
    )