from rag.retrieval.bm25 import BM25Retriever


def main():

    bm25 = BM25Retriever()

    while True:

        query = input("\nQuery (exit to quit): ").strip()

        if query.lower() == "exit":
            break

        if not query:
            print("Please enter a query.")
            continue

        docs = bm25.search(query)

        print("\nResults")
        print("=" * 70)

        if not docs:
            print("No results found.")
            continue

        for i, (doc, score) in enumerate(
            docs,
            start=1
        ):

            print(f"\nRank {i}")

            print(
                f"BM25 Score : {score:.4f}"
            )

            print(
                f"Metadata   : {doc.metadata}"
            )

            print(
                f"Content    : "
                f"{doc.page_content[:300]}"
            )


if __name__ == "__main__":
    main()