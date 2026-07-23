import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)


class DocumentLoader:
    """
    Responsible only for loading documents
    from supported file formats.
    """

    def load(
        self,
        file_path: str
    ):

        if not file_path:

            raise ValueError(
                "File path cannot be empty."
            )


        if not os.path.exists(
            file_path
        ):

            raise FileNotFoundError(
                f"File not found: {file_path}"
            )


        extension = os.path.splitext(
            file_path
        )[1].lower()


        if extension == ".pdf":

            loader = PyPDFLoader(
                file_path
            )


        elif extension == ".txt":

            loader = TextLoader(
                file_path,
                encoding="utf-8"
            )


        elif extension == ".docx":

            loader = Docx2txtLoader(
                file_path
            )


        else:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )


        return loader.load()


def load_documents(
    file_path: str
):

    loader = DocumentLoader()

    return loader.load(
        file_path
    )