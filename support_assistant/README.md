# Module 3 — Support Assistant (`/support_assistant`)

This module builds a Zepto support assistant using a local RAG pipeline.
It prepares Zepto policy documents for semantic retrieval and connects
that knowledge base to LangGraph, structured output, FastAPI, and Docker.

**Pipeline:** `documents → chunking → embeddings → ChromaDB → retrieval → generation → API → Docker`

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
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Task 1 — Document Ingestion, Embeddings & ChromaDB

### What it does

Loads the 8 supplied Zepto support documents, creates embeddings using
`all-MiniLM-L6-v2`, and stores them in ChromaDB for semantic retrieval.

### Chunking

Each document is treated as **one chunk**.

**Why?** The documents are short and each focuses on one main policy
topic. Splitting them further would fragment the context and create
unnecessary embeddings.

```text
8 documents → 8 chunks
```

### Embeddings

Model:

```text
all-MiniLM-L6-v2
```

Each chunk produces a **384-dimensional embedding**.

### ChromaDB

The embeddings are stored in the support document collection using
cosine similarity.

**Why ChromaDB?** It provides the vector store used for semantic retrieval.

### Re-runnable ingestion

`upsert()` is used instead of `add()` so the ingestion script can be run
again without creating duplicate document IDs.

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

```text
Retrieved Context + User Question
              ↓
       Structured Prompt
              ↓
        LLM / Mock LLM
```

The prompt contains role, context, task, format, length, negative
constraint, and a few-shot example.

### Why use a structured prompt?

It makes the assistant's expected behaviour clear and consistent.

### Why include `{context}`?

It provides the location where relevant information retrieved from
ChromaDB is inserted.

### Why include a negative constraint?

It helps prevent unsupported policies, prices, delivery times, or refund
rules from being invented.

### Why include a few-shot example?

It demonstrates the expected relationship between context, question,
answer, and sources.

### Testing

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\prompts.py
```

No LLM is required because this test validates the prompt template itself.

### Task 2 status

- [x] Create reusable prompt template
- [x] Add role
- [x] Add context placeholder
- [x] Add task instructions
- [x] Define response format
- [x] Define response length
- [x] Add negative constraint
- [x] Add few-shot example
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

`retriever.py` converts the question into an embedding and searches the
ChromaDB collection.

The top 3 relevant documents are returned.

**Why top 3?** It provides relevant context while avoiding unnecessary
documents and excessive context.

### Why separate retrieval from the graph?

Retrieval is kept in `retriever.py` and workflow logic in `graph.py`,
making the components easier to maintain and test.

### LangGraph

```text
START
  ↓
retrieve
  ↓
generate
  ↓
END
```

### Mock LLM

`mock_llm.py` provides a deterministic local replacement for a real LLM.

**Why?** The workflow can be tested without an external API key, network
dependency, or model cost.

### Testing

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .
etriever.py
python .\mock_llm.py
python .\graph.py
```

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

Defines the structured response format using Pydantic.

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

```text
answer       → Customer-facing answer
sources      → Documents used for the answer
confidence   → Confidence score between 0 and 1
```

### Why use Pydantic?

It provides a fixed schema so the application produces predictable data.

### Why include `sources`?

Sources make the response traceable to the retrieved knowledge base.
A list is used because one question may require multiple documents.

### Why validate `confidence`?

The value is restricted to `0.0–1.0` to prevent invalid confidence values.

### Testing

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\schemas.py
```

### Task 4 status

- [x] Create Pydantic response model
- [x] Add `answer`
- [x] Add `sources`
- [x] Add `confidence`
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

FastAPI provides an HTTP interface and automatically generates interactive
API documentation.

### Why `POST /ask`?

The customer question is sent as request data and processed by the
support workflow.

Example:

```json
{
  "question": "How long does Zepto delivery take?"
}
```

### Why validate the request?

`AskRequest` requires a non-empty question so invalid input does not reach
the retrieval workflow.

### Why reuse LangGraph?

The API calls the existing workflow instead of duplicating retrieval and
generation logic.

### Testing

```powershell
cd "D:\Projects\Capstone project\support_assistant"
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Test:

```json
{
  "question": "How long does Zepto delivery take?"
}
```

The `/ask` endpoint was successfully tested through Swagger.

### Task 5 status

- [x] Create FastAPI application
- [x] Create `AskRequest`
- [x] Validate user questions
- [x] Create `POST /ask`
- [x] Connect `/ask` to LangGraph
- [x] Use `SupportResponse`
- [x] Add root endpoint
- [x] Test API
- [x] Test invalid input
- [x] Verify Swagger documentation

---

## Task 6 — Docker Packaging

### What it does

Packages the complete support assistant into a Docker image so it can run
in an isolated and reproducible environment.

```text
Docker Image
    ↓
Python + Dependencies
    ↓
Project Files
    ↓
ingest.py
    ↓
ChromaDB
    ↓
FastAPI
    ↓
/ask
```

### Why Docker?

The application depends on Python packages, an embedding model, and
ChromaDB. Docker packages the environment so it does not depend on the
host Python environment.

### Dockerfile

The Dockerfile uses:

```text
python:3.11-slim
```

The Dockerfile also runs:

```dockerfile
RUN python ingest.py
```

**Why?** ChromaDB is generated from the source documents. Running
ingestion while building the image makes the image self-contained.

### `.dockerignore`

The `.dockerignore` excludes:

```text
venv/
__pycache__/
*.pyc
.git/
.gitignore
```

This prevents unnecessary local files from being copied into the image.

### Requirements

A `requirements.txt` must exist inside `support_assistant`.

**Why?** Docker uses `support_assistant` as its build context, so the
dependency file must be available inside that directory.

### Complete Task 6 command sequence

Run these commands **in order**.

#### 1. Go to the module

```powershell
cd "D:\Projects\Capstone project\support_assistant"
```

#### 2. Check Docker

```powershell
docker --version
```

#### 3. Check Docker Engine

```powershell
docker info
```

The output must contain both:

```text
Client:
...
Server:
...
```

If the Server section cannot connect, start Docker Desktop and wait until
the Docker Engine is running.

#### 4. Check WSL 2

```powershell
wsl -l -v
```

Docker Desktop on Windows should have a working WSL 2 backend.

#### 5. Check required files

```powershell
Get-ChildItem Dockerfile,.dockerignore,requirements.txt
```

All three files should exist inside `support_assistant`.

#### 6. Verify the Dockerfile

```powershell
Get-Content .\Dockerfile
```

It should contain:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python ingest.py

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

#### 7. Verify `.dockerignore`

```powershell
Get-Content .\.dockerignore
```

It should contain:

```text
venv/
__pycache__/
*.pyc
.git/
.gitignore
```

#### 8. Check Docker Hub connectivity

```powershell
nslookup registry-1.docker.io
```

Then:

```powershell
docker pull python:3.11-slim
```

This confirms Docker can reach Docker Hub before the full build.

#### 9. Build the image

```powershell
docker build -t zepto-support-assistant .
```

Wait for:

```text
FINISHED
```

and:

```text
naming to docker.io/library/zepto-support-assistant:latest
```

#### 10. Verify the image

```powershell
docker images zepto-support-assistant
```

#### 11. Run the container

```powershell
docker run --rm -p 7860:7860 zepto-support-assistant
```

Keep this terminal open.

#### 12. Test the root endpoint

Open another PowerShell:

```powershell
curl http://127.0.0.1:7860/
```

Expected:

```json
{
  "message": "Zepto Support Assistant API is running"
}
```

#### 13. Open Swagger

Open:

```text
http://127.0.0.1:7860/docs
```

The Swagger page should show:

```text
GET /
POST /ask
```

#### 14. Test `/ask`

In Swagger:

```text
POST /ask
→ Try it out
```

Use:

```json
{
  "question": "How long does Zepto delivery take?"
}
```

Click **Execute**.

The response should contain:

```text
answer
sources
confidence
```

#### 15. Optional direct `/ask` test

```powershell
curl -X POST "http://127.0.0.1:7860/ask" -H "Content-Type: application/json" -d "{"question":"How long does Zepto delivery take?"}"
```

### Common Task 6 errors

#### `docker` is not recognized

```powershell
docker --version
```

Install/start Docker Desktop and open a new PowerShell.

#### Docker API/daemon cannot be reached

Start Docker Desktop, wait for the engine, then run:

```powershell
docker info
```

#### `requirements.txt` not found

Make sure it exists inside the module:

```powershell
Get-ChildItem .
equirements.txt
```

Run the build from:

```text
D:\Projects\Capstone project\support_assistant
```

#### `registry-1.docker.io ... no such host`

Run:

```powershell
nslookup registry-1.docker.io
docker pull python:3.11-slim
```

If the pull succeeds, run the build again.

#### `RUN python ingest.py` fails

Check:

```powershell
Get-ChildItem .\docs
```

and test locally:

```powershell
python .\ingest.py
```

### Task 6 status

- [x] Install Docker Desktop
- [x] Enable WSL 2 backend
- [x] Create `Dockerfile`
- [x] Create `.dockerignore`
- [x] Keep `requirements.txt` inside the module
- [x] Build Docker image
- [x] Run `ingest.py` during image build
- [x] Generate ChromaDB inside the image
- [ ] Run Docker container
- [ ] Verify Swagger inside container
- [ ] Verify `/ask` inside container

---

## Module 3 — Task Progress

| Task | Component | Status |
|---|---|---|
| Task 1 | Document ingestion, embeddings & ChromaDB | Completed |
| Task 2 | Structured prompt template | Completed |
| Task 3 | LangGraph workflow & retrieval | Completed |
| Task 4 | Structured Pydantic output | Completed |
| Task 5 | FastAPI `/ask` endpoint | Completed |
| Task 6 | Docker packaging | In Progress |
| Task 7 | Final documentation & validation | Pending |
