# Module 3 — Support Assistant (`/support_assistant`)

This module builds a Zepto support assistant using a local RAG pipeline.
It prepares Zepto policy documents for semantic retrieval and later connects
that knowledge base to LangGraph, an LLM, structured output, and FastAPI.

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
├── chroma_db/
├── ingest.py
├── prompts.py
├── retriever.py
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

Loads the 8 supplied Zepto support documents, creates embeddings using
`all-MiniLM-L6-v2`, and stores them in ChromaDB for semantic retrieval.

### Chunking

Each document is treated as **one chunk**.

**Why?** The supplied documents are short and each document focuses on
one main policy topic. Splitting them into multiple chunks would
unnecessarily increase the number of embeddings and fragment the context.

```text
8 documents → 8 chunks
```

### Embeddings

Model:

```text
all-MiniLM-L6-v2
```

Each chunk produces a **384-dimensional embedding**.

**Why this model?** It is the embedding model specified by the assignment
and is lightweight enough for local execution.

### ChromaDB

The embeddings are stored in:

```text
zepto_support_docs
```

with **cosine similarity**.

**Why ChromaDB?** It is the vector store specified by the assignment and
will later be used to retrieve relevant policy information.

### Re-runnable ingestion

`upsert()` is used instead of `add()`.

**Why?** The ingestion script can be run multiple times without creating
duplicate document IDs.

### Task 1 flow

```text
8 Documents
    ↓
1 Chunk / Document
    ↓
all-MiniLM-L6-v2
    ↓
384D Embeddings
    ↓
ChromaDB
```

### Task 1 status

- [x] Create 8 policy documents
- [x] Load documents
- [x] Use one chunk per document
- [x] Generate embeddings
- [x] Store embeddings in ChromaDB
- [x] Configure cosine similarity
- [x] Make ingestion safely re-runnable

---

## Task 2 — Structured Prompt Template

### What it does

Creates a reusable prompt template in `prompts.py`.

The template accepts:

- Retrieved context
- User question

and combines them with clear instructions for the support assistant.

```text
Retrieved Context + User Question
              ↓
       Structured Prompt
              ↓
        LLM / Mock LLM
```

### Prompt structure

The prompt contains:

```text
Role
Context
Task
Format
Length
Negative Constraint
Few-shot Example
```

### Why use a structured prompt?

A structured prompt makes the assistant's expected behaviour clear and
consistent. The same template can be reused for different customer
questions instead of manually creating a new prompt each time.

### Why include a context placeholder?

The `{context}` placeholder is where relevant information retrieved from
ChromaDB will be inserted in the later RAG workflow.

This keeps the retrieved knowledge separate from the prompt instructions.

### Why include a negative constraint?

The prompt instructs the assistant not to invent policies, prices,
delivery times, refund rules, or other unsupported information.

This helps keep future answers grounded in the retrieved Zepto documents.

### Why include a few-shot example?

The example shows the expected relationship between:

```text
Context
   ↓
Question
   ↓
Answer
   ↓
Source
```

This gives the model a concrete example of the expected response style.

### Why define the response format?

The prompt requests:

```text
Answer: <concise answer>
Sources: <relevant source document names>
```

This establishes a consistent response format that can later be converted
into the structured output required by the support assistant.

### Why include a length instruction?

The assistant is designed for customer support, so responses should be
concise and directly address the customer's question rather than produce
unnecessary explanations.

### Task 2 testing

`prompts.py` contains a built-in test block.

Running:

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\prompts.py
```

formats a sample context and question and prints the generated system
prompt and user message.

The test confirms that:

```text
Context + Question
       ↓
Prompt Template
       ↓
Formatted Messages
```

are working correctly.

No LLM is required for this test because Task 2 only validates the prompt
template. LLM integration will be handled in a later task.

### Task 2 status

- [x] Create reusable prompt template
- [x] Add role
- [x] Add context placeholder
- [x] Add task instructions
- [x] Define response format
- [x] Define response length
- [x] Add negative constraint
- [x] Add few-shot example
- [x] Add prompt formatting function
- [x] Add built-in prompt test
- [x] Test prompt formatting

---

## Module 3 — Task Progress

| Task | Component | Status |
|---|---|---|
| Task 1 | Document ingestion, embeddings & ChromaDB | Completed |
| Task 2 | Structured prompt template | Completed |
| Task 3 | LangGraph workflow & retrieval | Pending |
| Task 4 | Structured Pydantic output | Pending |
| Task 5 | FastAPI `/ask` endpoint | Pending |
| Task 6 | Docker packaging | Pending |
| Task 7 | Final documentation & validation | Pending |