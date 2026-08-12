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

**Why this model?** It is lightweight and suitable for local semantic
search.

### ChromaDB

The embeddings are stored in the support document collection using
cosine similarity.

**Why ChromaDB?** It provides the vector store used for semantic retrieval.

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

### Why use a structured prompt?

A structured prompt makes the assistant's expected behaviour clear and
consistent. The same template can be reused for different customer
questions.

### Why include a context placeholder?

The `{context}` placeholder is where relevant information retrieved from
ChromaDB will be inserted into the RAG workflow.

### Why include a negative constraint?

The prompt instructs the assistant not to invent unsupported policies,
prices, delivery times, refund rules, or other information.

### Why include a few-shot example?

The example demonstrates the expected relationship between context,
question, answer, and sources.

### Why define the response format?

A consistent format makes the result easier to process in later stages.

### Testing

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\prompts.py
```

No LLM is required for this test because Task 2 validates the prompt
template itself.

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
the ChromaDB collection.

The top 3 relevant documents are returned.

**Why top 3?** It provides relevant context while avoiding unnecessary
documents and excessive context.

### Why separate retrieval from the graph?

Retrieval is kept in `retriever.py`, while workflow logic is kept in
`graph.py`. This keeps the components easier to maintain and test.

### LangGraph

The workflow contains:

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

**Why use a Mock LLM?** It allows the workflow to be tested without an
external API key, network dependency, or model cost.

### Testing

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\retriever.py
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

```text
answer       → Customer-facing answer
sources      → Documents used for the answer
confidence   → Confidence score between 0 and 1
```

### Why use Pydantic?

LLM responses are normally unstructured text. Pydantic provides a fixed
schema so the application produces predictable data.

### Why include `sources`?

The sources make the response traceable to the retrieved knowledge base.
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

FastAPI provides an HTTP interface for the support assistant and
automatically generates interactive API documentation.

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

`AskRequest` requires a non-empty question so invalid input does not
reach the retrieval workflow.

### Why use `response_model=SupportResponse`?

It ensures the API returns a consistent structure:

```text
answer
sources
confidence
```

### Why reuse LangGraph?

The API calls the existing workflow instead of duplicating retrieval and
generation logic.

### Testing

Start the API:

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

Packages the complete support assistant into a Docker image so the
application can run in an isolated and reproducible environment.

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
ChromaDB. Docker packages the environment so the application can be run
without depending on the host Python environment.

### Dockerfile

The Dockerfile uses:

```text
python:3.11-slim
```

**Why?** It provides Python in a relatively lightweight base image.

The Dockerfile also runs:

```dockerfile
RUN python ingest.py
```

**Why?** The ChromaDB collection is generated from the source documents.
Running ingestion while building the image makes the image self-contained.

### `.dockerignore`

The `.dockerignore` excludes:

```text
venv/
__pycache__/
*.pyc
.git/
.gitignore
```

**Why?** These files are not required inside the image and excluding them
keeps the build context smaller.

### Requirements

The module keeps a local:

```text
support_assistant/requirements.txt
```

**Why?** Docker builds using `support_assistant` as the build context, so
the dependency file must be available inside that directory.

### Complete Task 6 command sequence

Run the commands below **in order**.

#### Step 1 — Go to the module

```powershell
cd "D:\Projects\Capstone project\support_assistant"
```

#### Step 2 — Confirm Docker is installed

```powershell
docker --version
```

#### Step 3 — Confirm Docker Engine is running

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

If the `Server` section reports that the Docker API/engine cannot be
reached, start Docker Desktop and wait until the engine is running before
continuing.

#### Step 4 — Check WSL

```powershell
wsl -l -v
```

Docker Desktop on Windows should have a working WSL 2 backend.

#### Step 5 — Check the required files

```powershell
Get-ChildItem Dockerfile,.dockerignore,requirements.txt
```

The three files should exist inside `support_assistant`.

#### Step 6 — Check the Dockerfile

```powershell
Get-Content .\Dockerfile
```

The Dockerfile should contain:

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

#### Step 7 — Check `.dockerignore`

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

#### Step 8 — Test Docker Hub connectivity

```powershell
nslookup registry-1.docker.io
```

Then:

```powershell
docker pull python:3.11-slim
```

**Why?** The Dockerfile needs the `python:3.11-slim` base image. This
command confirms that Docker can reach Docker Hub before starting the full
build.

If the image is already available, Docker may report:

```text
Status: Image is up to date for python:3.11-slim
```

#### Step 9 — Build the Docker image

```powershell
docker build -t zepto-support-assistant .
```

**Why?** The `.` means the current `support_assistant` directory is used
as the Docker build context.

Wait until the build finishes successfully.

A successful build should contain:

```text
FINISHED
```

and:

```text
naming to docker.io/library/zepto-support-assistant:latest
```

#### Step 10 — Verify the image

```powershell
docker images zepto-support-assistant
```

The image should be listed.

#### Step 11 — Run the container

```powershell
docker run --rm -p 7860:7860 zepto-support-assistant
```

**Why `-p 7860:7860`?**

The first `7860` is the Windows host port and the second `7860` is the
container port used by Uvicorn.

Keep this terminal running.

#### Step 12 — Test the root endpoint

Open another PowerShell window and run:

```powershell
curl http://127.0.0.1:7860/
```

Expected response:

```json
{
  "message": "Zepto Support Assistant API is running"
}
```

#### Step 13 — Open Swagger

Open in the browser:

```text
http://127.0.0.1:7860/docs
```

The Swagger page should show:

```text
GET /
POST /ask
```

#### Step 14 — Test `/ask`

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

#### Step 15 — Optional direct API test

From another PowerShell:

```powershell
curl -X POST "http://127.0.0.1:7860/ask" -H "Content-Type: application/json" -d "{\"question\":\"How long does Zepto delivery take?\"}"
```

### Common Task 6 errors

#### Error: `docker is not recognized`

Docker Desktop/CLI is not installed or available in PATH.

Check:

```powershell
docker --version
```

#### Error: Docker API/daemon cannot be reached

Start Docker Desktop and wait for the Docker Engine to run.

Then:

```powershell
docker info
```

#### Error: `requirements.txt not found`

Make sure the file exists inside the module:

```powershell
Get-ChildItem .\requirements.txt
```

The build must be executed from:

```text
D:\Projects\Capstone project\support_assistant
```

#### Error: `registry-1.docker.io ... no such host`

Check:

```powershell
nslookup registry-1.docker.io
docker pull python:3.11-slim
```

If `docker pull` succeeds, run the build again.

#### Error during `RUN python ingest.py`

Check that the source documents exist:

```powershell
Get-ChildItem .\docs
```

Also make sure the same ingestion command works locally:

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
- [x] Run Docker container
- [x] Verify Swagger inside container
- [x] Verify `/ask` inside container

---

## Task 7 — Final Documentation & Validation

### What it does

Performs the final validation of Module 3 and confirms that all
components work together from document ingestion to the Dockerized
FastAPI endpoint.

### Final flow

```text
Documents
   ↓
Embeddings
   ↓
ChromaDB
   ↓
Retriever
   ↓
LangGraph
   ↓
Pydantic
   ↓
FastAPI
   ↓
Docker
   ↓
POST /ask
```

### Why perform final validation?

Each task was tested individually during development. Task 7 verifies
that the complete system still works together after all components have
been integrated.

### Validation performed

```text
ingest.py       → Document ingestion tested
retriever.py    → Semantic retrieval tested
graph.py        → LangGraph workflow tested
schemas.py      → Structured output tested
FastAPI         → /ask endpoint tested
Docker          → Container build tested
Docker /ask     → Final end-to-end API tested
```

### Step 1 — Validate ingestion

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\ingest.py
```

### Step 2 — Validate retrieval

```powershell
python .\retriever.py
```

### Step 3 — Validate LangGraph

```powershell
python .\graph.py
```

### Step 4 — Validate Pydantic

```powershell
python .\schemas.py
```

### Step 5 — Validate FastAPI

```powershell
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

Stop the server with:

```text
CTRL + C
```

### Step 6 — Build the final Docker image

```powershell
docker build -t zepto-support-assistant .
```

### Step 7 — Run the final container

```powershell
docker run --rm -p 7860:7860 zepto-support-assistant
```

### Step 8 — Test the Docker root endpoint

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

### Step 9 — Test Docker Swagger

Open:

```text
http://127.0.0.1:7860/docs
```

### Step 10 — Test Docker `/ask`

Use:

```json
{
  "question": "How long does Zepto delivery take?"
}
```

The final response should contain:

```text
answer
sources
confidence
```

### Step 11 — Test another question

```json
{
  "question": "Can I cancel my order?"
}
```

This verifies that the application is not working only for one question.

### Final validation status

- [x] Document ingestion works
- [x] Embeddings work
- [x] ChromaDB works
- [x] Retrieval works
- [x] LangGraph workflow works
- [x] Pydantic validation works
- [x] FastAPI works
- [x] Docker image builds
- [x] Docker container runs
- [x] Docker Swagger works
- [x] Docker `/ask` works
- [x] Final documentation completed
- [x] Final validation completed

### Task 7 status

**Completed ✅**

---

## Module 3 — Final Task Progress

| Task | Component | Status |
|---|---|---|
| Task 1 | Document ingestion, embeddings & ChromaDB | Completed |
| Task 2 | Structured prompt template | Completed |
| Task 3 | LangGraph workflow & retrieval | Completed |
| Task 4 | Structured Pydantic output | Completed |
| Task 5 | FastAPI `/ask` endpoint | Completed |
| Task 6 | Docker packaging | Completed |
| Task 7 | Final documentation & validation | Completed |

## Module 3 Status

**Completed ✅**

The Support Assistant module has been tested from document ingestion
through the Dockerized `/ask` endpoint.

---
