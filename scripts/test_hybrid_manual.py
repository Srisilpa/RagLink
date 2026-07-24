from rag.retrieval.hybrid import HybridRetriever

retriever = HybridRetriever()

while True:

    query = input("\nQuestion (exit to quit): ")

    if query.lower() == "exit":
        break

    docs = retriever.search(query)

    print("\nRetrieved Documents")
    print("=" * 70)

    for i, (doc, score) in enumerate(docs, start=1):

        print(f"\nRank {i}")
        print("Score:", score)
        print(doc.metadata)
        print(doc.page_content[:300])