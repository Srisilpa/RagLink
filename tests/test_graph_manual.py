from rag.langgraph.graph import graph

while True:

    question = input("\nAsk a question (exit to quit): ")

    if question.lower() == "exit":
        break

    result = graph.invoke(
        {
            "question": question
        }
    )

    print("\nAnswer")
    print("=" * 70)
    print(result["answer"])