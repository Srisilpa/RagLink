from langchain_text_splitters import RecursiveCharacterTextSplitter



def split_documents(documents):

    # Remove empty pages/content

    cleaned_documents = []

    for doc in documents:

        text = doc.page_content.strip()

        if text:
            doc.page_content = text
            cleaned_documents.append(doc)



    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )


    chunks = splitter.split_documents(
        cleaned_documents
    )


    return chunks