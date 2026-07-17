from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.rerank import Reranker

hybrid = HybridRetriever()
reranker = Reranker()

while True:

    query = input("\nQuestion (exit to quit): ")

    if query.lower() == "exit":
        break

    results = hybrid.search(query)
    documents = [doc for doc, _ in results]

    ranked = reranker.rerank(query, documents)

    print("\nTop Reranked Documents")
    print("=" * 70)

    for i, doc in enumerate(ranked, start=1):
        print(f"\nRank {i}")
        print(doc.metadata)
        print(doc.page_content[:300])