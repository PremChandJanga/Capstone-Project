from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from task3.retriever import retrieve_documents
from task3.mock_llm import mock_llm


class SupportState(TypedDict, total=False):
    question: str
    context: str
    sources: list[str]
    answer: str


def retrieve_node(state: SupportState):
    """
    Retrieve relevant policy documents from ChromaDB.
    """

    results = retrieve_documents(
        state["question"],
        top_k=3
    )

    context = "\n\n".join(
        result["text"]
        for result in results
    )

    sources = [
        result["source"]
        for result in results
    ]

    return {
        "context": context,
        "sources": sources,
    }


def generate_node(state: SupportState):
    """
    Generate an answer using the deterministic mock LLM.
    """

    answer = mock_llm(
        question=state["question"],
        context=state["context"]
    )

    return {
        "answer": answer
    }


# --------------------------------------------------
# Build LangGraph
# --------------------------------------------------

builder = StateGraph(SupportState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("generate", generate_node)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

support_graph = builder.compile()


# --------------------------------------------------
# Test the graph
# --------------------------------------------------

if __name__ == "__main__":

    question = "How long does Zepto delivery take?"

    result = support_graph.invoke(
        {
            "question": question
        }
    )

    print("\n" + "=" * 60)
    print("TASK 3 — LANGGRAPH WORKFLOW TEST")
    print("=" * 60)

    print("\nQuestion:")
    print(question)

    print("\nRetrieved Sources:")
    for source in result["sources"]:
        print(f"- {source}")

    print("\nContext:")
    print(result["context"])

    print("\nAnswer:")
    print(result["answer"])

    print("\n" + "=" * 60)
    print("LANGGRAPH WORKFLOW TEST PASSED")
    print("=" * 60)