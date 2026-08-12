# Module 3 — Support Assistant (`/support_assistant`)

This module builds a Zepto support assistant using a local RAG pipeline.
It prepares Zepto policy documents for semantic retrieval and connects
that knowledge base to LangGraph, structured output, and FastAPI.

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
├── mock_llm.py
├── graph.py
├── schemas.py
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

### Why `chroma_db/` is not committed

The ChromaDB directory is generated locally from the source documents and
`ingest.py`. It can therefore be recreated whenever required.

Keeping it in `.gitignore` avoids committing generated database files while
keeping the source needed to reproduce the database.

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

### How to run

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\ingest.py
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

Run:

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\prompts.py
```

The test formats a sample context and question and prints the generated
system prompt and user message.

No LLM is required for this test because Task 2 only validates the prompt
template.

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

## Task 3 — LangGraph Workflow, Retrieval & Mock LLM

### What it does

Connects the ChromaDB knowledge base to a LangGraph workflow.

```text
User Question
      ↓
Retrieve relevant documents
      ↓
Build context
      ↓
MOCK_LLM
      ↓
Answer
```

### Retrieval

`retriever.py` converts the user question into an embedding and searches
the `zepto_support_docs` ChromaDB collection.

The top 3 relevant documents are returned.

**Why top 3?** The assistant needs the most relevant policy information,
not the complete document collection. Limiting the results reduces
irrelevant context while still providing multiple relevant sources.

### Why separate retrieval from the graph?

Retrieval is kept in `retriever.py`, while workflow logic is kept in
`graph.py`.

This separation makes the application easier to maintain and allows the
retrieval strategy to be changed without rewriting the workflow.

### LangGraph

The workflow contains two nodes:

```text
START
  ↓
retrieve
  ↓
generate
  ↓
END
```

The `retrieve` node gets relevant policy documents from ChromaDB.

The `generate` node receives the question and retrieved context and
passes them to the Mock LLM.

**Why LangGraph?** It provides an explicit state-based workflow that can
later be extended with routing, additional nodes, and different execution
paths.

### Mock LLM

`mock_llm.py` provides a deterministic local replacement for a real LLM.

**Why use a Mock LLM?** It allows the complete workflow to be tested
without an external API key, network dependency, or model cost.

The Mock LLM is used to verify that the generation stage of the workflow
is reached.

### Testing

Run:

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\retriever.py
python .\mock_llm.py
python .\graph.py
```

For example:

```text
Question:
How long does Zepto delivery take?
```

The retrieval stage should return relevant policy documents, including the
delivery policy when appropriate.

### Task 3 status

- [x] Create ChromaDB retriever
- [x] Generate query embeddings
- [x] Retrieve top 3 relevant documents
- [x] Create LangGraph state
- [x] Add retrieval node
- [x] Add generation node
- [x] Add deterministic Mock LLM
- [x] Connect LangGraph nodes
- [x] Test retrieval
- [x] Test complete workflow

---

## Task 4 — Structured Pydantic Output

### What it does

Defines the structured response format for the support assistant using
Pydantic.

```text
LangGraph Result
      ↓
Pydantic Validation
      ↓
SupportResponse
      ↓
answer + sources + confidence
```

### Response schema

The `SupportResponse` model contains:

```text
answer       → Customer-facing answer
sources      → Documents used for the answer
confidence   → Confidence score between 0 and 1
```

### Why use Pydantic?

LLM responses are normally unstructured text. Pydantic provides a fixed
schema so that the support assistant produces predictable data that can
later be returned through the FastAPI endpoint.

### Why include `sources`?

The retrieval stage identifies the documents used for a question.
Including these document names makes the response traceable to the
knowledge base.

A list is used because one question may require information from multiple
documents.

### Why validate `confidence`?

The confidence value is restricted to the range `0.0` to `1.0`.

This prevents invalid values such as negative confidence or values greater
than 1.

### Testing

Run:

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\schemas.py
```

The test creates a valid `SupportResponse` and prints the structured
object and JSON representation.

An additional validation test confirms that an invalid confidence value
is rejected by Pydantic.

### Task 4 status

- [x] Create Pydantic response model
- [x] Add `answer` field
- [x] Add `sources` field
- [x] Add `confidence` field
- [x] Validate confidence range
- [x] Test structured JSON output
- [x] Test invalid confidence validation

---

## Task 5 — FastAPI `/ask` Endpoint

### What it does

Exposes the support assistant through a REST API.

```text
Client
  ↓
POST /ask
  ↓
FastAPI
  ↓
LangGraph
  ↓
Retrieval + Generation
  ↓
Pydantic Response
  ↓
JSON
```

### Why FastAPI?

FastAPI provides a simple HTTP interface for the support assistant and
automatically generates interactive API documentation.

### Why `POST /ask`?

The endpoint receives a customer question as request data and sends it
through the support workflow.

Example request:

```json
{
  "question": "How long does Zepto delivery take?"
}
```

### Why validate the request?

`AskRequest` uses Pydantic validation and requires the question to contain
at least one character.

This prevents empty requests from reaching the retrieval workflow.

### Why use `response_model=SupportResponse`?

The response uses the Pydantic schema created in Task 4.

This ensures that the API returns a consistent structure containing:

```text
answer
sources
confidence
```

### Why reuse LangGraph?

The API does not duplicate retrieval or generation logic. It calls the
existing LangGraph workflow from Task 3.

This keeps the API layer separate from the AI workflow and makes the
components easier to maintain.

### Why is confidence currently `1.0`?

The current workflow uses a deterministic Mock LLM and does not calculate
a calibrated confidence score. Therefore, `1.0` is used only to satisfy
the current structured response schema. It should not be interpreted as a
real probability.

### Testing

Start the API:

```powershell
cd "D:\Projects\Capstone project\support_assistant"
uvicorn app:app --reload
```

FastAPI should start at:

```text
http://127.0.0.1:8000
```

Open the interactive documentation:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI should show:

```text
GET  /
POST /ask
```

Test `/ask` using:

```json
{
  "question": "How long does Zepto delivery take?"
}
```

The endpoint successfully returns the validated `SupportResponse` JSON.

### Task 5 status

- [x] Create FastAPI application
- [x] Create `AskRequest` model
- [x] Validate user questions
- [x] Create `POST /ask`
- [x] Connect `/ask` to LangGraph
- [x] Use `SupportResponse`
- [x] Add root endpoint
- [x] Test API
- [x] Test invalid input
- [x] Verify Swagger documentation

---

## Module 3 — Task Progress

| Task | Component | Status |
|---|---|---|
| Task 1 | Document ingestion, embeddings & ChromaDB | Completed |
| Task 2 | Structured prompt template | Completed |
| Task 3 | LangGraph workflow & retrieval | Completed |
| Task 4 | Structured Pydantic output | Completed |
| Task 5 | FastAPI `/ask` endpoint | Completed |
| Task 6 | Docker packaging | Pending |
| Task 7 | Final documentation & validation | Pending |