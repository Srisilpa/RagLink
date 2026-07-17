from rag.retrieval.bm25 import BM25Retriever


bm25 = BM25Retriever()

while True:

    query = input("\nQuery (exit to quit): ")

    if query.lower() == "exit":
        break

    docs = bm25.search(query)

    print("\nResults")
    print("=" * 70)

    for i, (doc, score) in enumerate(docs, start=1):

        print(f"\nRank {i}")

        print(f"BM25 Score : {score:.4f}")

        print(doc.metadata)

        print(doc.page_content[:300])