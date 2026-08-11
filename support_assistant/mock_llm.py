def mock_llm(question: str, context: str):
    """
    Deterministic mock LLM for local testing.

    This does not call an external LLM.
    """

    return (
        "MOCK_LLM: Based on the retrieved Zepto policy information, "
        f"the answer to your question '{question}' is provided by "
        "the retrieved context."
    )


if __name__ == "__main__":

    question = "How long does Zepto delivery take?"

    context = (
        "Zepto delivers grocery and household essentials "
        "within 10 to 30 minutes of order confirmation."
    )

    answer = mock_llm(question, context)

    print("\n" + "=" * 60)
    print("MOCK LLM TEST")
    print("=" * 60)

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)

    print("\n" + "=" * 60)