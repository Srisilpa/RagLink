from rag.retrieval.retriever import Retriever


def print_results(results):
    print("\nRetrieved Documents")
    print("=" * 80)

    for index, (doc, score) in enumerate(results, start=1):
        print(f"\nRank: {index}")
        print(f"Distance Score: {score:.4f}")

        print("\nMetadata:")
        print(doc.metadata)

        print("\nContent:")
        print("-" * 80)
        print(doc.page_content[:400])
        print("-" * 80)


def main():
    retriever = Retriever()

    while True:
        query = input("\nAsk a question (type 'exit' to quit): ")

        if query.lower() == "exit":
            print("Exiting...")
            break

        try:
            results = retriever.retrieve(
                query=query,
                return_k=5,
                fetch_k=10
            )

            print_results(results)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()