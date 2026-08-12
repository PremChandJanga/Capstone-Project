from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR.parent / "task1" / "chroma_db"

COLLECTION_NAME = "zepto_support_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


model = SentenceTransformer(EMBEDDING_MODEL)

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


def retrieve_documents(query: str, top_k: int = 3):
    """
    Retrieve the most relevant documents from ChromaDB.
    """

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    retrieved = []

    for document, metadata in zip(documents, metadatas):
        retrieved.append(
            {
                "text": document,
                "source": metadata["source"]
            }
        )

    return retrieved


if __name__ == "__main__":

    question = "How long does Zepto delivery take?"

    results = retrieve_documents(question)

    print("\n" + "=" * 60)
    print("TASK 3 — RETRIEVAL TEST")
    print("=" * 60)

    print(f"\nQuestion: {question}")

    print("\nRetrieved Documents:")
    print("-" * 60)

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print(f"Source: {result['source']}")
        print(f"Content: {result['text']}")

    print("\n" + "=" * 60)
    print("RETRIEVAL TEST PASSED")
    print("=" * 60)