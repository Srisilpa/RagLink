import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)


class DocumentLoader:
    """
    Responsible for loading documents from
    supported file formats and enriching them
    with standard metadata.
    """

    def load(
        self,
        file_path: str
    ):

        # ==========================================
        # VALIDATE FILE PATH
        # ==========================================

        if not file_path:

            raise ValueError(
                "File path cannot be empty."
            )

        # ==========================================
        # CHECK FILE EXISTS
        # ==========================================

        if not os.path.exists(
            file_path
        ):

            raise FileNotFoundError(

                f"File not found: {file_path}"

            )

        # ==========================================
        # GET FILE INFORMATION
        # ==========================================

        extension = os.path.splitext(
            file_path
        )[1].lower()

        file_name = os.path.basename(
            file_path
        )

        # ==========================================
        # LOAD DOCUMENT
        # ==========================================

        if extension == ".pdf":

            loader = PyPDFLoader(
                file_path
            )

            file_type = "pdf"

        elif extension == ".txt":

            loader = TextLoader(

                file_path,

                encoding="utf-8"

            )

            file_type = "txt"

        elif extension == ".docx":

            loader = Docx2txtLoader(
                file_path
            )

            file_type = "docx"

        else:

            raise ValueError(

                f"Unsupported file type: "
                f"{extension}"

            )

        # ==========================================
        # LOAD DOCUMENTS
        # ==========================================

        documents = loader.load()

        # ==========================================
        # DETERMINE DOCUMENT CATEGORY
        # ==========================================

        document_type = (
            self._get_document_type(
                file_path
            )
        )

        # ==========================================
        # ENRICH METADATA
        # ==========================================

        for document in documents:

            # Make sure metadata exists
            if document.metadata is None:

                document.metadata = {}

            # --------------------------------------
            # SOURCE
            # --------------------------------------

            document.metadata[
                "source"
            ] = file_path

            # --------------------------------------
            # FILE NAME
            # --------------------------------------

            document.metadata[
                "file_name"
            ] = file_name

            # --------------------------------------
            # FILE TYPE
            # --------------------------------------

            document.metadata[
                "file_type"
            ] = file_type

            # --------------------------------------
            # DOCUMENT TYPE
            # --------------------------------------

            document.metadata[
                "document_type"
            ] = document_type

        return documents

    # ==========================================
    # DETERMINE DOCUMENT TYPE
    # ==========================================

    def _get_document_type(
        self,
        file_path: str
    ):

        # ------------------------------------------
        # Normalize path
        # ------------------------------------------

        normalized_path = (
            file_path
            .replace(
                "\\",
                "/"
            )
            .lower()
        )

        # ------------------------------------------
        # Company documents
        # ------------------------------------------

        if "/company/" in normalized_path:

            return "company"

        # ------------------------------------------
        # Project documents
        # ------------------------------------------

        if "/projects/" in normalized_path:

            return "project"

        # ------------------------------------------
        # Default
        # ------------------------------------------

        return "general"


def load_documents(
    file_path: str
):

    loader = DocumentLoader()

    return loader.load(
        file_path
    )