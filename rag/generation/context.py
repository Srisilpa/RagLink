class ContextBuilder:
    """
    Builds clean context from retrieved documents.
    """

    def build(
        self,
        documents,
        max_documents: int = 5
    ):

        if not documents:

            return ""


        unique_content = []

        seen = set()


        for doc in documents:

            content = (
                doc.page_content
                .strip()
            )


            if not content:

                continue


            if content in seen:

                continue


            seen.add(
                content
            )


            unique_content.append(
                content
            )


            if len(
                unique_content
            ) >= max_documents:

                break


        return "\n\n".join(
            unique_content
        )