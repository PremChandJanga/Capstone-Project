from langchain_core.prompts import ChatPromptTemplate


# --------------------------------------------------
# Support Assistant Prompt
# --------------------------------------------------

SUPPORT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
ROLE:
You are a Zepto customer support assistant.

CONTEXT:
Use the retrieved Zepto policy information below to answer the user.

{context}

TASK:
Answer the user's question using only the provided context.
If the context does not contain enough information, clearly state that
the available policy information does not provide the answer.

FORMAT:
Answer: <concise answer>
Sources: <relevant source document names>

LENGTH:
Keep the answer concise and directly address the user's question.

CONSTRAINT:
Do not use information that is not supported by the provided context.
Do not invent Zepto policies, prices, delivery times, refund rules,
or any other information.

FEW-SHOT EXAMPLE:

Context:
Zepto delivers grocery and household essentials within 10 to 30 minutes
of order confirmation, depending on the delivery zone and current order
volume.

Question:
How long does Zepto delivery take?

Answer:
Zepto delivery typically takes 10 to 30 minutes after order confirmation,
depending on the delivery zone and current order volume.

Sources:
doc_01.txt
""",
        ),
        (
            "human",
            "Question: {question}",
        ),
    ]
)


def format_support_prompt(context: str, question: str):
    """
    Insert the retrieved context and user question
    into the support assistant prompt.
    """

    return SUPPORT_PROMPT.format_messages(
        context=context,
        question=question,
    )


# --------------------------------------------------
# Task 2 Test
# --------------------------------------------------

if __name__ == "__main__":

    test_context = (
        "Zepto delivers grocery and household essentials "
        "within 10 to 30 minutes of order confirmation."
    )

    test_question = "How long does Zepto delivery take?"

    messages = format_support_prompt(
        context=test_context,
        question=test_question,
    )

    print("\n" + "=" * 60)
    print("TASK 2 — PROMPT TEMPLATE TEST")
    print("=" * 60)

    print("\nSYSTEM PROMPT:")
    print("-" * 60)
    print(messages[0].content)

    print("\n" + "-" * 60)
    print("USER MESSAGE:")
    print("-" * 60)
    print(messages[1].content)

    print("\n" + "=" * 60)
    print("PROMPT TEMPLATE TEST PASSED")
    print("=" * 60)