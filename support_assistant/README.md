# Module 3 — Support Assistant (`/support_assistant`)

This module builds a Zepto support assistant using a local RAG pipeline.
It prepares Zepto policy documents for semantic retrieval and later connects
that knowledge base to LangGraph, a mock/real LLM, structured output, and
FastAPI.

**Pipeline:** `documents → chunking → embeddings → ChromaDB → retrieval → generation → API`

```text
support_assistant/
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
├── ingest.py
├── retriever.py
├── prompts.py
├── graph.py
├── schemas.py
├── mock_llm.py
├── app.py
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

The files are added progressively as each task is completed.

---

## Task 1 — Document Ingestion, Embeddings & ChromaDB

### What it does

Loads the 8 supplied Zepto support documents, converts each document into
an embedding using `all-MiniLM-L6-v2`, and stores the embeddings in a
ChromaDB collection named `zepto_support_docs`.

**Task 1 flow:**

```text
8 policy documents
        ↓
Document loading
        ↓
1 chunk per document
        ↓
all-MiniLM-L6-v2
        ↓
384-dimensional embeddings
        ↓
ChromaDB
```

### Why 8 separate document files

Each file represents one policy area, such as delivery, refunds,
membership, tracking, cancellation, damaged items, gift cards, or
customer support.

Keeping them separate preserves the source of the information, which is
useful later when the assistant returns document sources with an answer.

### Why one chunk per document

The supplied documents are short and each one focuses on a single policy
topic. Splitting a short, coherent document into several smaller chunks
would fragment the context and create additional embeddings without a
significant retrieval benefit.

Therefore:

```text
8 documents → 8 chunks
```

A more detailed chunking strategy would be more useful for a much larger
document containing many unrelated sections.

### Why `all-MiniLM-L6-v2`

`all-MiniLM-L6-v2` is the embedding model specified for this task. It is
also lightweight enough to run locally.

Each chunk produces a **384-dimensional vector**.

### Why ChromaDB

ChromaDB is the vector store required for this task. It allows the later
retrieval stage to find policy information using semantic similarity
rather than relying only on exact keyword matches.

The collection uses **cosine similarity**, which is suitable for comparing
the semantic direction of embedding vectors.

### Why `upsert()` during ingestion

The ingestion script uses `upsert()` with stable document IDs such as
`doc_01`.

This makes the script safe to run repeatedly: existing documents are
updated instead of being inserted as duplicates.

### Why `chroma_db/` is not committed

The ChromaDB directory is generated locally from the source documents and
`ingest.py`. It can therefore be recreated whenever required.

Keeping it in `.gitignore` avoids committing generated database files to
the repository while keeping the source needed to reproduce the database.

### How to run

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\ingest.py
```

Expected result:

```text
Loaded 8 documents.
Documents stored: 8
Embedding dimension: 384
```

### Task 1 status

- [x] Create 8 policy documents
- [x] Load documents
- [x] Use one chunk per document
- [x] Generate `all-MiniLM-L6-v2` embeddings
- [x] Store embeddings in ChromaDB
- [x] Configure cosine similarity
- [x] Make ingestion safely re-runnable

---

## Module 3 — Task Progress

| Task | Component | Status |
|---|---|---|
| Task 1 | Document ingestion, embeddings & ChromaDB | Completed |
| Task 2 | Structured prompt template | Pending |
| Task 3 | LangGraph workflow & retrieval | Pending |
| Task 4 | Structured Pydantic output | Pending |
| Task 5 | FastAPI `/ask` endpoint | Pending |
| Task 6 | Docker packaging | Pending |
| Task 7 | Final documentation & validation | Pending |