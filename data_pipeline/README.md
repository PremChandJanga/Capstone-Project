# Module 1 — Data Pipeline (`/data_pipeline`)

Scrapes product-style data (books, standing in for Zepto's catalog category)
from books.toscrape.com, cleans it, converts currency, loads it into a
relational SQLite database, and queries it with both SQL and pandas.

Pipeline stages: **scrape → clean → convert → store → query**

Each stage is a separate script so the pipeline can be run/debugged one
piece at a time.

---

## Stage 1 — Scrape (`scrape.py`)

**What it does**
Scrapes book listings from three categories: `Nonfiction`, `Romance`,
`Sequential Art`. For each book it captures: `title`, `price`,
`star_rating`, `availability`, `category`. Output is saved as raw,
unmodified text to `data/raw/books_raw.csv`.

**Design decisions**
- Category URLs are looked up dynamically from the homepage sidebar
  instead of being hardcoded, since books.toscrape.com assigns each
  category a numeric ID in its URL (e.g. `romance_8`) that isn't
  predictable or guaranteed stable.
- Pagination is followed automatically by checking for a "next" link
  on each page, rather than assuming a fixed number of pages per
  category — categories have different book counts.
- No cleaning or type conversion happens in this stage. Fields are
  stored exactly as scraped (e.g. price as `"£51.77"`, rating as the
  word `"Three"`) so the scrape stage stays focused on data collection
  only. Cleaning is handled separately in Stage 2.
- A `time.sleep(0.5)` delay is added between page requests as basic
  scraping etiquette.

**How to run**
```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\scrape.py
```

**Output**
`data_pipeline/data/raw/books_raw.csv` — raw scraped rows across the
3 required categories, ≥60 books total.

---

## Stage 2 — Clean (`clean.py`)
*(to be added)*

## Stage 3 — Convert (`convert.py`)
*(to be added)*

## Stage 4 — Store (`store.py`)
*(to be added)*

## Stage 5 — Query (`query.py`)
*(to be added)*