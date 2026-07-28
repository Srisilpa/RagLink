import os
import pickle
import hashlib


from rag.ingestion.processor import (
    IngestionProcessor
)

from rag.embeddings.embedding_model import (
    get_embedding_model
)

from rag.vectorstore.chroma import (
    add_documents_to_chroma,
    delete_document_from_chroma,
    update_document_in_chroma,
    rebuild_vectorstore
)

from rag.retrieval.bm25 import (
    rebuild_bm25_index
)


# =========================================================
# PATHS
# =========================================================

CHUNKS_PATH = "data/chunks.pkl"

EMBEDDINGS_PATH = "data/chunk_embeddings.pkl"


# =========================================================
# SINGLETON COMPONENTS
# =========================================================

_processor = None

_embedding_model = None


# =========================================================
# GET PROCESSOR
# =========================================================

def get_processor():

    global _processor

    if _processor is None:

        _processor = IngestionProcessor(

            chunk_size=200,

            chunk_overlap=50

        )

    return _processor


# =========================================================
# GET EMBEDDING MODEL
# =========================================================

def get_embeddings():

    global _embedding_model

    if _embedding_model is None:

        _embedding_model = get_embedding_model()

    return _embedding_model


# =========================================================
# DOCUMENT ID
# =========================================================

def get_document_id(
    file_path
):

    absolute_path = os.path.abspath(

        file_path

    )

    return hashlib.md5(

        absolute_path.encode(

            "utf-8"

        )

    ).hexdigest()


# =========================================================
# ADD SOURCE METADATA
# =========================================================

def add_source_metadata(
    chunks,
    file_path,
    document_id
):

    relative_path = os.path.relpath(

        file_path,

        "media"

    )

    document_type = detect_document_type(

        file_path

    )

    for index, chunk in enumerate(

        chunks

    ):

        metadata = (

            chunk.metadata

            or {}

        )

        metadata.update({

            "document_id":

                str(

                    document_id

                ),

            "source":

                relative_path,

            "file_name":

                os.path.basename(

                    file_path

                ),

            "document_type":

                document_type,

            "chunk_id":

                f"{document_id}_{index}",

        })

        chunk.metadata = metadata

    return chunks


# =========================================================
# DETECT DOCUMENT TYPE
# =========================================================

def detect_document_type(
    file_path
):

    normalized_path = os.path.normpath(

        file_path

    )

    parts = normalized_path.split(

        os.sep

    )

    lowered_parts = [

        part.lower()

        for part in parts

    ]

    if "company" in lowered_parts:

        return "company"

    if "projects" in lowered_parts:

        return "project"

    return "other"


# =========================================================
# PROCESS DOCUMENT
# =========================================================

def process_document(
    file_path,
    document_id
):

    if not os.path.exists(

        file_path

    ):

        raise FileNotFoundError(

            f"Document not found: "

            f"{file_path}"

        )

    processor = get_processor()

    result = processor.process(

        file_path

    )

    chunks = result.get(

        "chunks",

        []

    )

    chunks = add_source_metadata(

        chunks,

        file_path,

        document_id

    )

    return chunks


# =========================================================
# LOAD ALL CHUNKS
# =========================================================

def load_all_chunks():

    if not os.path.exists(

        CHUNKS_PATH

    ):

        return []

    with open(

        CHUNKS_PATH,

        "rb"

    ) as f:

        return pickle.load(

            f

        )


# =========================================================
# SAVE ALL CHUNKS
# =========================================================

def save_all_chunks(
    chunks
):

    os.makedirs(

        "data",

        exist_ok=True

    )

    with open(

        CHUNKS_PATH,

        "wb"

    ) as f:

        pickle.dump(

            chunks,

            f

        )


# =========================================================
# REBUILD EMBEDDINGS FILE
# =========================================================

def rebuild_embeddings_file(
    chunks
):

    embedding_model = get_embeddings()

    texts = [

        chunk.page_content

        for chunk in chunks

    ]

    if not texts:

        embeddings = []

    else:

        embeddings = (

            embedding_model

            .embed_documents(

                texts

            )

        )

    os.makedirs(

        "data",

        exist_ok=True

    )

    with open(

        EMBEDDINGS_PATH,

        "wb"

    ) as f:

        pickle.dump(

            embeddings,

            f

        )


# =========================================================
# REBUILD CHROMADB
# =========================================================

def rebuild_chroma():

    chunks = load_all_chunks()

    embedding_model = get_embeddings()

    return rebuild_vectorstore(

        documents=chunks,

        embedding_model=embedding_model

    )


# =========================================================
# REBUILD BM25 DATA
# =========================================================

def rebuild_bm25():

    chunks = load_all_chunks()

    rebuild_bm25_index(

        chunks

    )


# =========================================================
# REBUILD EVERYTHING
# =========================================================

def rebuild_indexes():

    chunks = load_all_chunks()

    print(

        f"\nRebuilding all RAG indexes "

        f"for {len(chunks)} chunks..."

    )

    # -----------------------------------------------------
    # REBUILD EMBEDDINGS FILE
    # -----------------------------------------------------

    rebuild_embeddings_file(

        chunks

    )

    # -----------------------------------------------------
    # REBUILD CHROMADB
    # -----------------------------------------------------

    rebuild_chroma()

    # -----------------------------------------------------
    # REBUILD BM25
    # -----------------------------------------------------

    rebuild_bm25()

    print(

        "\nAll RAG indexes rebuilt successfully."

    )


# =========================================================
# ADD OR UPDATE DOCUMENT
# =========================================================

def index_document(
    file_path,
    document_id
):

    document_id = str(

        document_id

    )

    print(

        f"\n============================================================"

    )

    print(

        "DOCUMENT INDEXING"

    )

    print(

        "============================================================"

    )

    print(

        f"Document ID: {document_id}"

    )

    print(

        f"File: {file_path}"

    )

    # =====================================================
    # PROCESS DOCUMENT
    # =====================================================

    new_chunks = process_document(

        file_path,

        document_id

    )

    print(

        f"Generated {len(new_chunks)} new chunks."

    )

    # =====================================================
    # LOAD EXISTING MASTER CHUNKS
    # =====================================================

    existing_chunks = load_all_chunks()

    # =====================================================
    # REMOVE OLD CHUNKS FROM MASTER LIST
    # =====================================================

    filtered_chunks = [

        chunk

        for chunk in existing_chunks

        if str(

            (chunk.metadata or {}).get(

                "document_id",

                ""

            )

        ) != document_id

    ]

    old_chunk_count = (

        len(existing_chunks)

        -

        len(filtered_chunks)

    )

    print(

        f"Existing chunks removed from master data: "

        f"{old_chunk_count}"

    )

    # =====================================================
    # UPDATE MASTER CHUNK LIST
    # =====================================================

    filtered_chunks.extend(

        new_chunks

    )

    save_all_chunks(

        filtered_chunks

    )

    print(

        f"Master chunk data updated."

        f" Total chunks: {len(filtered_chunks)}"

    )

    # =====================================================
    # GET EMBEDDING MODEL
    # =====================================================

    embedding_model = get_embeddings()

    # =====================================================
    # UPDATE CHROMADB
    # =====================================================

    print(

        "\nUpdating ChromaDB..."

    )

    chroma_result = update_document_in_chroma(

        document_id=document_id,

        documents=new_chunks,

        embedding_model=embedding_model

    )

    # =====================================================
    # REBUILD BM25 DATA
    # =====================================================

    print(

        "\nUpdating BM25 index..."

    )

    rebuild_bm25_index(

        filtered_chunks

    )

    # =====================================================
    # REBUILD EMBEDDINGS FILE
    # =====================================================

    rebuild_embeddings_file(

        filtered_chunks

    )

    # =====================================================
    # COMPLETE
    # =====================================================

    print(

        "\n============================================================"

    )

    print(

        "DOCUMENT INDEXING COMPLETED"

    )

    print(

        "============================================================"

    )

    print(

        f"Document ID: {document_id}"

    )

    print(

        f"Old chunks: {old_chunk_count}"

    )

    print(

        f"New chunks: {len(new_chunks)}"

    )

    print(

        f"Total chunks: {len(filtered_chunks)}"

    )

    if chroma_result:

        print(

            f"ChromaDB removed: "

            f"{chroma_result.get('removed', 0)}"

        )

        print(

            f"ChromaDB added: "

            f"{chroma_result.get('added', 0)}"

        )

    print(

        "BM25 index updated."

    )

    print(

        "Embeddings file updated."

    )

    print(

        "============================================================"

    )

    return len(

        new_chunks

    )


# =========================================================
# DELETE DOCUMENT
# =========================================================

def delete_document_from_index(
    document_id
):

    document_id = str(

        document_id

    )

    print(

        f"\n============================================================"

    )

    print(

        "DYNAMIC DOCUMENT DELETION"

    )

    print(

        "============================================================"

    )

    print(

        f"Document ID: {document_id}"

    )

    # =====================================================
    # LOAD MASTER CHUNKS
    # =====================================================

    existing_chunks = load_all_chunks()

    # =====================================================
    # REMOVE DOCUMENT FROM MASTER CHUNKS
    # =====================================================

    filtered_chunks = [

        chunk

        for chunk in existing_chunks

        if str(

            (chunk.metadata or {}).get(

                "document_id",

                ""

            )

        ) != document_id

    ]

    removed_count = (

        len(existing_chunks)

        -

        len(filtered_chunks)

    )

    print(

        f"Master chunks removed: "

        f"{removed_count}"

    )

    # =====================================================
    # SAVE UPDATED MASTER CHUNKS
    # =====================================================

    save_all_chunks(

        filtered_chunks

    )

    # =====================================================
    # GET EMBEDDING MODEL
    # =====================================================

    embedding_model = get_embeddings()

    # =====================================================
    # DELETE FROM CHROMADB
    # =====================================================

    print(

        "\nRemoving document from ChromaDB..."

    )

    chroma_removed = (

        delete_document_from_chroma(

            document_id,

            embedding_model

        )

    )

    # =====================================================
    # REBUILD BM25 DATA
    # =====================================================

    print(

        "\nUpdating BM25 index..."

    )

    rebuild_bm25_index(

        filtered_chunks

    )

    # =====================================================
    # REBUILD EMBEDDINGS FILE
    # =====================================================

    rebuild_embeddings_file(

        filtered_chunks

    )

    # =====================================================
    # COMPLETE
    # =====================================================

    print(

        "\n============================================================"

    )

    print(

        "DOCUMENT DELETION COMPLETED"

    )

    print(

        "============================================================"

    )

    print(

        f"Document ID: {document_id}"

    )

    print(

        f"Master chunks removed: {removed_count}"

    )

    print(

        f"ChromaDB chunks removed: {chroma_removed}"

    )

    print(

        f"Remaining chunks: {len(filtered_chunks)}"

    )

    print(

        "BM25 index updated."

    )

    print(

        "Embeddings file updated."

    )

    print(

        "============================================================"

    )

    return removed_count