# Module 3 — Support Assistant

## Overview

This module builds a small GenAI support assistant for Zepto.

The required baseline uses a fully local and deterministic workflow.
The document corpus is embedded and indexed in ChromaDB so that
relevant policy information can be retrieved for user queries.

---

# Task 1 — Document Ingestion, Embeddings and ChromaDB

## Objective

Load the eight supplied Zepto policy documents, create one chunk per
document, generate embeddings using `all-MiniLM-L6-v2`, and store the
embeddings in a ChromaDB collection.

## Document Corpus

The module contains eight documents:

1. Delivery Policy
2. Returns & Refunds
3. Membership Tiers
4. Order Tracking
5. Order Cancellation Policy
6. Damaged or Missing Items
7. Gift Cards
8. Customer Support Hours

They are stored in:

```text
docs/
├── doc_01.txt
├── doc_02.txt
├── doc_03.txt
├── doc_04.txt
├── doc_05.txt
├── doc_06.txt
├── doc_07.txt
└── doc_08.txt