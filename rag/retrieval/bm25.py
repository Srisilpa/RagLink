import os
import pickle

from rank_bm25 import BM25Okapi


# =========================================================
# DEFAULT BM25 DATA PATH
# =========================================================

DEFAULT_CHUNKS_PATH = "data/chunks.pkl"


class BM25Retriever:
    """
    BM25 keyword-based retriever.

    Features:
        - Keyword-based retrieval
        - Metadata filtering
        - Multiple allowed filter values
        - Runtime index reload
        - Document-level chunk deletion
        - Persistent BM25 chunk storage

    Stored format:

        data/chunks.pkl

    Each item in the pickle file should be a
    LangChain Document object.

    Expected metadata example:

        {
            "document_id": "20",
            "document_type": "project",
            "source": "media/Projects/example.pdf",
            "chunk_id": "20_0"
        }
    """

    def __init__(
        self,
        chunks_path: str = DEFAULT_CHUNKS_PATH
    ):

        self.chunks_path = chunks_path

        # -------------------------------------------------
        # INITIALIZE EMPTY STATE
        # -------------------------------------------------

        self.documents = []

        self.tokenized_documents = []

        self.bm25 = None

        # -------------------------------------------------
        # LOAD INDEX
        # -------------------------------------------------

        self._load_index()

    # =====================================================
    # LOAD INDEX
    # =====================================================

    def _load_index(self):
        """
        Load BM25 documents from disk and build
        the in-memory BM25 index.
        """

        # -------------------------------------------------
        # FILE DOES NOT EXIST
        # -------------------------------------------------

        if not os.path.exists(
            self.chunks_path
        ):

            self.documents = []

            self.tokenized_documents = []

            self.bm25 = None

            print(
                "BM25 chunks file not found. "
                "Starting with empty BM25 index."
            )

            return

        # -------------------------------------------------
        # LOAD DOCUMENTS
        # -------------------------------------------------

        try:

            with open(
                self.chunks_path,
                "rb"
            ) as f:

                documents = pickle.load(
                    f
                )

        except Exception as e:

            raise RuntimeError(

                "Failed to load BM25 chunks file: "

                f"{e}"

            )

        # -------------------------------------------------
        # VALIDATE
        # -------------------------------------------------

        if documents is None:

            documents = []

        self.documents = documents

        # -------------------------------------------------
        # BUILD INDEX
        # -------------------------------------------------

        self._build_index()

        print(

            f"BM25 index loaded: "
            f"{len(self.documents)} chunks."

        )

    # =====================================================
    # BUILD INDEX
    # =====================================================

    def _build_index(self):
        """
        Build the in-memory BM25 index from
        self.documents.
        """

        # -------------------------------------------------
        # TOKENIZE DOCUMENTS
        # -------------------------------------------------

        self.tokenized_documents = [

            self._tokenize(
                document.page_content
            )

            for document in self.documents

        ]

        # -------------------------------------------------
        # EMPTY INDEX
        # -------------------------------------------------

        if not self.tokenized_documents:

            self.bm25 = None

            return

        # -------------------------------------------------
        # CREATE BM25 INDEX
        # -------------------------------------------------

        self.bm25 = BM25Okapi(

            self.tokenized_documents

        )

    # =====================================================
    # TOKENIZATION
    # =====================================================

    @staticmethod
    def _tokenize(
        text: str
    ):
        """
        Basic BM25 tokenization.
        """

        if not text:

            return []

        return (

            text.lower()
            .split()

        )

    # =====================================================
    # METADATA FILTER
    # =====================================================

    def _matches_filters(
        self,
        document,
        filters: dict = None
    ):
        """
        Check whether a document matches
        all requested metadata filters.

        Example:

            filters={
                "document_type": "project"
            }

        Multiple values:

            filters={
                "document_type": [
                    "project",
                    "company"
                ]
            }
        """

        # -------------------------------------------------
        # NO FILTERS
        # -------------------------------------------------

        if not filters:

            return True

        # -------------------------------------------------
        # DOCUMENT METADATA
        # -------------------------------------------------

        metadata = (

            document.metadata

            or {}

        )

        # -------------------------------------------------
        # CHECK EACH FILTER
        # -------------------------------------------------

        for key, expected_value in filters.items():

            actual_value = metadata.get(
                key
            )

            # ---------------------------------------------
            # MULTIPLE ALLOWED VALUES
            # ---------------------------------------------

            if isinstance(
                expected_value,
                list
            ):

                if actual_value not in expected_value:

                    return False

            # ---------------------------------------------
            # SINGLE VALUE
            # ---------------------------------------------

            else:

                if actual_value != expected_value:

                    return False

        # -------------------------------------------------
        # ALL FILTERS MATCHED
        # -------------------------------------------------

        return True

    # =====================================================
    # RETRIEVE
    # =====================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: dict = None
    ):
        """
        Retrieve documents using BM25.

        Returns:

            [
                (Document, score),
                ...
            ]
        """

        # -------------------------------------------------
        # EMPTY QUERY
        # -------------------------------------------------

        if not query or not query.strip():

            return []

        # -------------------------------------------------
        # VALIDATE TOP K
        # -------------------------------------------------

        if top_k <= 0:

            raise ValueError(

                "top_k must be greater than 0."

            )

        # -------------------------------------------------
        # EMPTY INDEX
        # -------------------------------------------------

        if not self.documents:

            return []

        if self.bm25 is None:

            return []

        # -------------------------------------------------
        # TOKENIZE QUERY
        # -------------------------------------------------

        query_tokens = self._tokenize(

            query

        )

        if not query_tokens:

            return []

        # -------------------------------------------------
        # CALCULATE BM25 SCORES
        # -------------------------------------------------

        scores = self.bm25.get_scores(

            query_tokens

        )

        # -------------------------------------------------
        # RANK DOCUMENTS
        # -------------------------------------------------

        ranked_indices = sorted(

            range(
                len(scores)
            ),

            key=lambda index:
                scores[index],

            reverse=True

        )

        # -------------------------------------------------
        # BUILD RESULTS
        # -------------------------------------------------

        results = []

        for index in ranked_indices:

            document = (

                self.documents[index]

            )

            # ---------------------------------------------
            # APPLY METADATA FILTER
            # ---------------------------------------------

            if not self._matches_filters(

                document,

                filters

            ):

                continue

            # ---------------------------------------------
            # GET SCORE
            # ---------------------------------------------

            score = scores[index]

            results.append(

                (

                    document,

                    float(score)

                )

            )

            # ---------------------------------------------
            # STOP AFTER TOP K
            # ---------------------------------------------

            if len(results) >= top_k:

                break

        return results

    # =====================================================
    # SEARCH ALIAS
    # =====================================================

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: dict = None
    ):

        return self.retrieve(

            query=query,

            top_k=top_k,

            filters=filters

        )

    # =====================================================
    # RELOAD INDEX
    # =====================================================

    def reload(self):
        """
        Reload the BM25 index from disk.

        This should be called after:

            - Document upload
            - Document deletion
            - BM25 index rebuild
        """

        print(

            "\nReloading BM25 runtime index..."

        )

        self._load_index()

        print(

            f"BM25 runtime index reloaded: "
            f"{len(self.documents)} chunks."

        )

    # =====================================================
    # DELETE DOCUMENT FROM MEMORY AND DISK
    # =====================================================

    def delete_document(
        self,
        document_id
    ):
        """
        Delete all BM25 chunks belonging to
        a specific document.

        Uses metadata:

            document_id

        Returns:

            Number of removed chunks.
        """

        # -------------------------------------------------
        # NORMALIZE DOCUMENT ID
        # -------------------------------------------------

        document_id = str(

            document_id

        )

        # -------------------------------------------------
        # CHECK CURRENT DOCUMENTS
        # -------------------------------------------------

        if not self.documents:

            return 0

        # -------------------------------------------------
        # FIND DOCUMENTS TO REMOVE
        # -------------------------------------------------

        remaining_documents = []

        removed_count = 0

        for document in self.documents:

            metadata = (

                document.metadata

                or {}

            )

            stored_document_id = metadata.get(

                "document_id"

            )

            # ---------------------------------------------
            # DELETE MATCHING DOCUMENT
            # ---------------------------------------------

            if (

                stored_document_id is not None

                and str(
                    stored_document_id
                ) == document_id

            ):

                removed_count += 1

                continue

            # ---------------------------------------------
            # KEEP OTHER DOCUMENTS
            # ---------------------------------------------

            remaining_documents.append(

                document

            )

        # -------------------------------------------------
        # UPDATE DOCUMENT LIST
        # -------------------------------------------------

        self.documents = (

            remaining_documents

        )

        # -------------------------------------------------
        # SAVE UPDATED CHUNKS
        # -------------------------------------------------

        self._save_documents()

        # -------------------------------------------------
        # REBUILD RUNTIME INDEX
        # -------------------------------------------------

        self._build_index()

        print(

            f"BM25 deleted document "
            f"{document_id}: "
            f"{removed_count} chunks removed."

        )

        return removed_count

    # =====================================================
    # SAVE DOCUMENTS
    # =====================================================

    def _save_documents(self):
        """
        Persist current BM25 documents to disk.
        """

        directory = os.path.dirname(

            self.chunks_path

        )

        if directory:

            os.makedirs(

                directory,

                exist_ok=True

            )

        with open(

            self.chunks_path,

            "wb"

        ) as f:

            pickle.dump(

                self.documents,

                f

            )

        print(

            f"BM25 data saved: "
            f"{len(self.documents)} chunks."

        )


# =========================================================
# REBUILD BM25 INDEX DATA
# =========================================================

def rebuild_bm25_index(
    chunks,
    chunks_path: str = DEFAULT_CHUNKS_PATH
):
    """
    Completely rebuild the persistent BM25
    chunk data.

    This does NOT create the BM25Okapi object itself.
    It saves the chunks to disk.

    The runtime retriever should then call:

        retriever.reload()
    """

    # -----------------------------------------------------
    # CREATE DIRECTORY
    # -----------------------------------------------------

    directory = os.path.dirname(

        chunks_path

    )

    if directory:

        os.makedirs(

            directory,

            exist_ok=True

        )

    # -----------------------------------------------------
    # SAVE CHUNKS
    # -----------------------------------------------------

    with open(

        chunks_path,

        "wb"

    ) as f:

        pickle.dump(

            chunks,

            f

        )

    print(

        f"BM25 index data rebuilt "
        f"with {len(chunks)} chunks."

    )


# =========================================================
# DELETE DOCUMENT DIRECTLY FROM BM25 DATA
# =========================================================

def delete_document_from_bm25(
    document_id,
    chunks_path: str = DEFAULT_CHUNKS_PATH
):
    """
    Remove all chunks belonging to a document
    directly from data/chunks.pkl.

    This is useful when document deletion is
    handled outside a long-running BM25Retriever
    instance.

    Returns:

        Number of removed chunks.
    """

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if not os.path.exists(

        chunks_path

    ):

        print(

            "BM25 chunks file does not exist."

        )

        return 0

    # -----------------------------------------------------
    # LOAD CHUNKS
    # -----------------------------------------------------

    with open(

        chunks_path,

        "rb"

    ) as f:

        documents = pickle.load(

            f

        )

    # -----------------------------------------------------
    # NORMALIZE ID
    # -----------------------------------------------------

    document_id = str(

        document_id

    )

    # -----------------------------------------------------
    # FILTER CHUNKS
    # -----------------------------------------------------

    remaining_documents = []

    removed_count = 0

    for document in documents:

        metadata = (

            document.metadata

            or {}

        )

        stored_document_id = metadata.get(

            "document_id"

        )

        if (

            stored_document_id is not None

            and str(
                stored_document_id
            ) == document_id

        ):

            removed_count += 1

            continue

        remaining_documents.append(

            document

        )

    # -----------------------------------------------------
    # SAVE UPDATED DATA
    # -----------------------------------------------------

    with open(

        chunks_path,

        "wb"

    ) as f:

        pickle.dump(

            remaining_documents,

            f

        )

    print(

        f"BM25 persistent deletion: "
        f"Document {document_id}, "
        f"removed {removed_count} chunks."

    )

    return removed_count