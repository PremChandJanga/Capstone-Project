from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_support_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# --------------------------------------------------
# Load documents
# --------------------------------------------------

def load_documents():
    documents = []

    for file_path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(
            {
                "id": file_path.stem,
                "text": text,
                "source": file_path.name,
            }
        )

    return documents


# --------------------------------------------------
# Create ChromaDB collection
# --------------------------------------------------

def create_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


# --------------------------------------------------
# Main ingestion pipeline
# --------------------------------------------------

def main():
    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Loading documents...")
    documents = load_documents()

    if len(documents) != 8:
        raise ValueError(
            f"Expected 8 documents, but found {len(documents)}."
        )

    print(f"Loaded {len(documents)} documents.")

    # One chunk per document is sufficient for this corpus.
    chunks = [document["text"] for document in documents]
    ids = [document["id"] for document in documents]
    metadatas = [
        {"source": document["source"]}
        for document in documents
    ]

    print("Generating embeddings...")

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
    ).tolist()

    print("Creating ChromaDB collection...")

    collection = create_collection()

    # Make the script safe to re-run.
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print("\nIngestion completed successfully.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Documents stored: {collection.count()}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Embedding dimension: {len(embeddings[0])}")
    print(f"ChromaDB location: {CHROMA_DIR}")


if __name__ == "__main__":
    main()