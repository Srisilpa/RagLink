from rag.pipeline import RAGPipeline


def test_leave_approval():

    pipeline = RAGPipeline()

    result = pipeline.ask(
        "Who approves my leave request?"
    )

    answer = result["answer"]

    print("\nANSWER:")
    print(answer)

    assert answer

    assert (
        "permanent remote work"
        not in answer.lower()
    )


def test_earned_leave():

    pipeline = RAGPipeline()

    result = pipeline.ask(
        "How many days of earned leave "
        "do confirmed employees receive?"
    )

    answer = result["answer"]

    print("\nANSWER:")
    print(answer)

    assert answer

    assert "15" in answer


def test_project_meridian_database():

    pipeline = RAGPipeline()

    result = pipeline.ask(
        "What database does Project Meridian use?"
    )

    answer = result["answer"]

    print("\nANSWER:")
    print(answer)

    assert answer

    assert "MySQL" in answer