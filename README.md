# Zepto Analytics & AI Capstone Project

## Overview

This capstone project is organized into three modules:

1. **Data Pipeline**
2. **Analytics**
3. **Support Assistant**

The three modules cover a progression from data collection and storage,
through analysis and machine learning, to a retrieval-based AI support
assistant.

```text
                         ZEpto Capstone Project
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
       Module 1              Module 2              Module 3
    Data Pipeline             Analytics        Support Assistant
             │                    │                    │
             ▼                    ▼                    ▼
      Scrape → Clean       EDA → Modeling       RAG → API
      → Convert → Store    → Evaluation         → Docker
      → Query
```

---

# Project Structure

```text
capstone-project/
│
├── data_pipeline/
│   ├── data/
│   │   ├── raw/
│   │   │   └── books_raw.csv
│   │   ├── processed/
│   │   │   ├── books_clean.csv
│   │   │   └── books_converted.csv
│   │   └── ...
│   ├── db/
│   │   └── books.db
│   ├── scrape.py
│   ├── clean.py
│   ├── convert.py
│   ├── store.py
│   ├── query.py
│   └── README.md
│
├── analytics/
│   ├── notebooks/
│   │   ├── 01_eda.ipynb
│   │   ├── 02_modeling.ipynb
│   │   └── titanic_survival_pipeline.joblib
│   ├── titanic.csv
│   ├── titanic_clean.csv
│   └── README.md
│
├── support_assistant/
│   ├── task1/
│   ├── task2/
│   ├── task3/
│   ├── task4/
│   ├── task5/
│   ├── task6/
│   ├── task7/
│   ├── .gitignore
│   └── README.md
│
└── README.md
```

> The exact generated files may change depending on execution. The
> structure above represents the current organization documented for the
> three modules.

---

# Module 1 — Data Pipeline

## Purpose

The Data Pipeline module performs the data-engineering workflow for
Zepto's analytics work.

The pipeline:

```text
Scrape → Clean → Convert → Store → Query
```

The module deliberately uses separate scripts for each stage so that
individual stages can be debugged and re-run independently. Intermediate
CSV files provide inspectable checkpoints between stages.

### Source

The scraping stage uses `books.toscrape.com` and collects books from:

- Nonfiction
- Romance
- Sequential Art

For each book it captures:

```text
title
price
star_rating
availability
category
```

The recorded raw data is written to:

```text
data_pipeline/data/raw/books_raw.csv
```

The pipeline produced **220 rows** in the documented run.

## Stage 1 — Scrape

File:

```text
data_pipeline/scrape.py
```

Technologies:

```text
requests
BeautifulSoup
```

The scraper dynamically discovers category URLs from the site's homepage
instead of relying on hardcoded category IDs. Pagination follows the
site's `next` link until no next page exists.

The response encoding is explicitly set to UTF-8 to avoid corruption of
the `£` currency symbol.

Run:

```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\scrape.py
```

Output:

```text
data_pipeline/data/raw/books_raw.csv
```

## Stage 2 — Clean

File:

```text
data_pipeline/clean.py
```

The raw values are converted into useful types:

```text
price         → price_gbp (float)
star_rating   → rating (1–5 integer)
availability  → in_stock (boolean)
```

Output:

```text
data_pipeline/data/processed/books_clean.csv
```

The cleaning stage handles malformed numeric values using documented
fallback rules and drops rows when a meaningful boolean value cannot be
determined.

Run:

```powershell
python data_pipeline\clean.py
```

## Stage 3 — Convert

File:

```text
data_pipeline/convert.py
```

Adds:

```text
price_inr
```

using the project-defined fixed conversion rate:

```text
1 GBP = 105.50 INR
```

The rate is fixed so the result remains deterministic and reproducible.

Output:

```text
data_pipeline/data/processed/books_converted.csv
```

Run:

```powershell
python data_pipeline\convert.py
```

## Stage 4 — Store

File:

```text
data_pipeline/store.py
```

Loads the converted data into a normalized SQLite database.

Database:

```text
data_pipeline/db/books.db
```

Main tables:

```text
categories
books
```

Relationship:

```text
categories.category_id
        │
        ▼
books.category_id
```

The database also contains three category views:

```text
view_sequential_art
view_romance
view_nonfiction
```

The documented run contains:

```text
categories → 3 rows
books      → 220 rows
views      → 3
```

Run:

```powershell
python data_pipeline\store.py
```

## Stage 5 — Query

File:

```text
data_pipeline/query.py
```

The query stage demonstrates:

| Query | SQL concepts |
|---|---|
| 1 | SELECT + WHERE |
| 2 | ORDER BY + LIMIT |
| 3 | DISTINCT |
| 4 | WHERE + BETWEEN |
| 5 | JOIN + ORDER BY + LIMIT |

The module also reproduces the SQL JOIN using `pandas.merge` and checks
that the SQL and pandas results match.

Run:

```powershell
python data_pipeline\query.py
```

## Module 1 Output

```text
Website
   ↓
Raw CSV
   ↓
Clean CSV
   ↓
Converted CSV
   ↓
SQLite database
   ↓
SQL + pandas queries
```

---

# Module 2 — Analytics

## Purpose

The Analytics module follows an analyst-to-data-scientist workflow:

```text
Profile → Clean → Explore → Model → Evaluate → Save Pipeline
```

The dataset used is the Titanic dataset.

The dataset is loaded with:

```python
sns.load_dataset("titanic")
```

This network load is performed once in the first EDA cell and immediately
saved as:

```text
titanic.csv
```

After that, the workflow uses the saved files rather than repeatedly
loading the dataset from the network.

## Structure

```text
analytics/
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_modeling.ipynb
│   └── titanic_survival_pipeline.joblib
├── titanic.csv
├── titanic_clean.csv
└── README.md
```

## Part A — Cleaning & EDA

Notebook:

```text
analytics/notebooks/01_eda.ipynb
```

Important cleaning operations include:

- Profiling the dataset
- Checking missing values
- Dropping `deck` because of very high missingness
- Imputing `age` using median values grouped by `pclass` and `sex`
- Removing redundant `embark_town`
- Removing rows with missing `embarked`
- Removing redundant `alive`
- Removing `adult_male`
- Removing redundant `class`

The EDA then covers:

```text
Univariate analysis
Bivariate analysis
Correlation analysis
Multivariate data story
Z-score standardization sanity check
```

The analysis examines variables such as:

```text
age
fare
sex
pclass
survived
sibsp
parch
```

The multivariate story examines survival using sex, class, age, and
family size together.

## Part B — Modeling

Notebook:

```text
analytics/notebooks/02_modeling.ipynb
```

The cleaned dataset is used for modeling.

### Classification

Three classifiers are trained:

```text
Logistic Regression
Decision Tree
Random Forest
```

The classification target is:

```text
survived
```

A stratified 80/20 train-test split is used with:

```text
random_state = 42
```

Evaluation includes:

```text
Accuracy
Precision
Recall
F1
AUC
Confusion Matrix
ROC Curve
```

### AUC comparison

| Model | AUC |
|---|---:|
| Logistic Regression | **0.87** |
| Random Forest | 0.82 |
| Decision Tree | 0.77 |

Logistic Regression achieved the strongest AUC in the documented
comparison.

### Class imbalance

Three Logistic Regression variants are compared:

```text
Baseline
class_weight="balanced"
SMOTE
```

Documented results:

| Variant | Precision | Recall | F1 |
|---|---:|---:|---:|
| Baseline | 0.8136 | 0.7059 | 0.7559 |
| class_weight=balanced | 0.7714 | **0.7941** | **0.7826** |
| SMOTE | 0.7727 | 0.7500 | 0.7612 |

The documented conclusion selects:

```text
class_weight="balanced"
```

for this comparison because it achieved the highest recall and F1.

### Random Forest tuning

GridSearchCV tunes:

```text
n_estimators
max_depth
max_features
```

The documented best combination is:

```text
max_depth = 5
max_features = sqrt
n_estimators = 300
```

Results:

```text
Best cross-validation accuracy = 0.8242
OOB score                     = 0.8284
```

### Regression side-task

A separate Linear Regression model predicts:

```text
fare
```

Metrics:

| Metric | Value |
|---|---:|
| MAE | 21.368 |
| RMSE | 42.421 |
| R² | 0.3255 |
| Adjusted R² | 0.2894 |

The residual analysis documents clear heteroscedasticity, consistent with
the heavy right-skew of `fare`.

### Final saved pipeline

The best-performing complete preprocessing + model pipeline is saved as:

```text
titanic_survival_pipeline.joblib
```

The complete pipeline includes preprocessing and the Logistic Regression
model rather than saving only the classifier.

The documented full-pipeline test accuracy is:

```text
0.8146
```

## Module 2 Output

```text
Titanic Dataset
      ↓
Cleaning
      ↓
EDA
      ↓
Feature Preparation
      ↓
Classification + Regression
      ↓
Model Evaluation
      ↓
Saved Complete Pipeline
```

---

# Module 3 — Support Assistant

## Purpose

The Support Assistant module builds a Zepto support assistant using a
local Retrieval-Augmented Generation (RAG) pipeline.

The module connects:

```text
Documents
   ↓
Embeddings
   ↓
ChromaDB
   ↓
Retrieval
   ↓
LangGraph
   ↓
Structured Output
   ↓
FastAPI
   ↓
Docker
```

The current task-based organization is:

```text
support_assistant/
│
├── task1/
│   ├── docs/
│   │   ├── doc_01.txt
│   │   ├── doc_02.txt
│   │   ├── doc_03.txt
│   │   ├── doc_04.txt
│   │   ├── doc_05.txt
│   │   ├── doc_06.txt
│   │   ├── doc_07.txt
│   │   └── doc_08.txt
│   ├── chroma_db/
│   └── ingest.py
│
├── task2/
│   └── prompts.py
│
├── task3/
│   ├── __init__.py
│   ├── retriever.py
│   ├── mock_llm.py
│   └── graph.py
│
├── task4/
│   ├── __init__.py
│   └── schemas.py
│
├── task5/
│   ├── __init__.py
│   └── app.py
│
├── task6/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── requirements.txt
│
├── task7/
│
├── .gitignore
└── README.md
```

## Task 1 — Document Ingestion

Eight Zepto policy documents are loaded.

Each document is treated as one chunk:

```text
8 documents → 8 chunks
```

Embedding model:

```text
all-MiniLM-L6-v2
```

Embedding dimension:

```text
384
```

Vector store:

```text
ChromaDB
```

Collection:

```text
zepto_support_docs
```

Similarity:

```text
cosine
```

The ingestion process uses `upsert()` so it can safely be re-run.

The current path configuration keeps the generated database under:

```text
task1/chroma_db/
```

Run:

```powershell
cd "D:\Projects\Capstone project\support_assistant"
python .\task1\ingest.py
```

## Task 2 — Prompt Template

File:

```text
task2/prompts.py
```

The prompt combines:

```text
Retrieved Context + User Question
              ↓
       Structured Prompt
              ↓
         LLM / Mock LLM
```

The prompt includes role, context, task instructions, response format,
length guidance, a negative constraint, and a few-shot example.

## Task 3 — Retrieval + LangGraph

Files:

```text
task3/retriever.py
task3/mock_llm.py
task3/graph.py
```

The retriever accesses:

```text
task1/chroma_db/
```

and returns the top 3 relevant documents.

The LangGraph workflow is:

```text
START
  ↓
retrieve
  ↓
generate
  ↓
END
```

`mock_llm.py` provides a deterministic local LLM replacement for workflow
testing without requiring an external LLM API.

Updated package imports use:

```python
from task3.retriever import retrieve_documents
from task3.mock_llm import mock_llm
```

## Task 4 — Structured Output

File:

```text
task4/schemas.py
```

The Pydantic response contains:

```text
answer
sources
confidence
```

`confidence` is restricted to the range:

```text
0.0 – 1.0
```

## Task 5 — FastAPI

File:

```text
task5/app.py
```

The API exposes:

```text
POST /ask
```

Example request:

```json
{
  "question": "How long does Zepto delivery take?"
}
```

The application imports:

```python
from task3.graph import support_graph
from task4.schemas import SupportResponse
```

Run:

```powershell
cd "D:\Projects\Capstone project\support_assistant"
uvicorn task5.app:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Task 6 — Docker

Docker files:

```text
task6/
├── Dockerfile
├── .dockerignore
└── requirements.txt
```

The Dockerfile uses:

```text
python:3.11-slim
```

The image copies the required task folders and runs Task 1 ingestion
inside the image to create its own ChromaDB.

Build from the `support_assistant` root:

```powershell
cd "D:\Projects\Capstone project\support_assistant"
docker build -f task6\Dockerfile -t zepto-support-assistant .
```

Run:

```powershell
docker run --rm -p 7860:7860 zepto-support-assistant
```

Swagger:

```text
http://127.0.0.1:7860/docs
```

The Docker image was successfully built as:

```text
zepto-support-assistant:latest
```

with the documented image information:

```text
Disk usage: 9.36 GB
Content size: 3.19 GB
```

## Task 7 — Final Validation

The complete support assistant was validated through:

```text
Document ingestion
        ↓
Embeddings
        ↓
ChromaDB
        ↓
Retrieval
        ↓
LangGraph
        ↓
Pydantic
        ↓
FastAPI
        ↓
Docker
        ↓
/ask
```

Module 3 status:

```text
Completed
```

---

# Overall Capstone Architecture

The three modules can be viewed as three independent but complementary
engineering layers:

```text
┌───────────────────────────────────────────────────────────┐
│                    CAPSTONE PROJECT                       │
└───────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌──────────────────┐
│   MODULE 1      │ │   MODULE 2      │ │    MODULE 3      │
│ Data Pipeline   │ │   Analytics     │ │ Support Assistant│
├─────────────────┤ ├─────────────────┤ ├──────────────────┤
│ Web Scraping    │ │ Data Cleaning   │ │ RAG              │
│ Data Cleaning   │ │ EDA             │ │ Embeddings       │
│ Currency        │ │ Visualization   │ │ ChromaDB         │
│ Conversion      │ │ Classification │ │ Retrieval        │
│ SQLite          │ │ Regression      │ │ LangGraph        │
│ SQL + Pandas    │ │ Evaluation      │ │ Pydantic         │
│                 │ │ Model Pipeline  │ │ FastAPI          │
│                 │ │                 │ │ Docker           │
└─────────────────┘ └─────────────────┘ └──────────────────┘
```

---

# Technologies Used

## Module 1 — Data Pipeline

```text
Python
Requests
BeautifulSoup
Pandas
SQLite
SQL
```

## Module 2 — Analytics

```text
Python
Pandas
NumPy
Seaborn
Matplotlib
Scikit-learn
imbalanced-learn / SMOTE
Joblib
Jupyter Notebook
```

## Module 3 — Support Assistant

```text
Python
Sentence Transformers
all-MiniLM-L6-v2
ChromaDB
LangGraph
LangChain Core
Pydantic
FastAPI
Uvicorn
Docker
```

---

# End-to-End Project Flow

```text
                    CAPSTONE PROJECT
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      DATA PIPELINE     ANALYTICS     SUPPORT ASSISTANT
          │                │                │
          ▼                ▼                ▼
      Web Data         Titanic Data     Policy Docs
          │                │                │
          ▼                ▼                ▼
       Cleaning          EDA           Embeddings
          │                │                │
          ▼                ▼                ▼
       Conversion       Modeling        ChromaDB
          │                │                │
          ▼                ▼                ▼
       SQLite           Evaluation      Retrieval
          │                │                │
          ▼                ▼                ▼
       SQL/Pandas      Saved Model      LangGraph
                                           │
                                           ▼
                                      Pydantic
                                           │
                                           ▼
                                        FastAPI
                                           │
                                           ▼
                                         Docker
```

---

# Running the Project

## Module 1

From the project root:

```powershell
python data_pipeline\scrape.py
python data_pipeline\clean.py
python data_pipeline\convert.py
python data_pipeline\store.py
python data_pipeline\query.py
```

## Module 2

Open:

```text
analytics/notebooks/01_eda.ipynb
analytics/notebooks/02_modeling.ipynb
```

Run the notebooks in order.

The EDA notebook creates:

```text
titanic.csv
titanic_clean.csv
```

The modeling notebook creates:

```text
titanic_survival_pipeline.joblib
```

## Module 3

From:

```text
D:\Projects\Capstone project\support_assistant
```

Run ingestion:

```powershell
python .\task1\ingest.py
```

Run the API:

```powershell
uvicorn task5.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

For Docker:

```powershell
docker build -f task6\Dockerfile -t zepto-support-assistant .
docker run --rm -p 7860:7860 zepto-support-assistant
```

Open:

```text
http://127.0.0.1:7860/docs
```

---

# Final Project Status

| Module | Area | Status |
|---|---|---|
| Module 1 | Data Pipeline | Completed |
| Module 2 | Analytics | Completed |
| Module 3 | Support Assistant | Completed |

## Overall Status

**Capstone Project — Completed**

The repository contains:

- A staged data pipeline from web scraping to SQLite and SQL/pandas
  querying.
- An analytics workflow covering cleaning, EDA, classification,
  regression, imbalance handling, hyperparameter tuning, evaluation, and
  model persistence.
- A RAG-based support assistant using embeddings, ChromaDB, retrieval,
  LangGraph, structured Pydantic output, FastAPI, and Docker.
