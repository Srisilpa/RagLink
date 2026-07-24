from rag.generation.llm import GroqLLM

llm = GroqLLM()

while True:

    question = input("\nQuestion (exit to quit): ")

    if question.lower() == "exit":
        break

    answer = llm.generate(question)

    print("\nAnswer")
    print("=" * 70)
    print(answer)