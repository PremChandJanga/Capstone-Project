Module 3 — Support Assistant

Overview

This module builds a Zepto support assistant using RAG, LangGraph,structured output, and FastAPI.

Task 1 — Document Ingestion, Embeddings & ChromaDB

Objective

Load the 8 Zepto support documents, create embeddings usingall-MiniLM-L6-v2, and store them in ChromaDB for semantic retrieval.

Documents

docs/
├── doc_01.txt
├── doc_02.txt
├── doc_03.txt
├── doc_04.txt
├── doc_05.txt
├── doc_06.txt
├── doc_07.txt
└── doc_08.txt

The documents contain Zepto policies such as delivery, refunds,membership, tracking, cancellation, damaged items, gift cards, andcustomer support.

Chunking

Each document is treated as one chunk.

Why? The supplied documents are short and each document contains onemain policy topic. Splitting them into multiple chunks would unnecessarilyincrease the number of embeddings and fragment the context.

8 documents → 8 chunks

Embeddings

Model:

all-MiniLM-L6-v2

Each chunk produces a 384-dimensional embedding.

Why this model? It is the embedding model specified by the assignmentand is lightweight enough for local execution.

ChromaDB

The embeddings are stored in:

zepto_support_docs

with cosine similarity.

Why ChromaDB? It is the vector store specified by the assignment andwill be used later to retrieve the most relevant policy chunks.

Re-runnable Ingestion

upsert() is used instead of add().

Why? The ingestion script can be run multiple times without creatingduplicate document IDs.

Architecture

8 Documents
    ↓
1 Chunk / Document
    ↓
all-MiniLM-L6-v2
    ↓
384D Embeddings
    ↓
ChromaDB

Run

cd "D:\Projects\Capstone project\support_assistant"
python .\ingest.py

Expected result:

Loaded 8 documents.
Documents stored: 8
Embedding dimension: 384

Task 1 Status

8 documents

Document loading

One chunk per document

Embeddings generated

ChromaDB collection created

Cosine similarity configured