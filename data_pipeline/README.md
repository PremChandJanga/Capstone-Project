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
- `resp.encoding = "utf-8"` is set explicitly on every request. Without
  this, `requests` occasionally mis-detects the page's encoding as
  ISO-8859-1, which corrupts the `£` symbol into garbled characters
  (e.g. `Â£`) before it's even written to the CSV. Setting it explicitly
  prevents that corruption at the source, rather than trying to clean it
  up later.

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

**What it does**
Reads `data/raw/books_raw.csv` and converts each raw field into a proper
type: `price` → `price_gbp` (float), `star_rating` → `rating` (int 1–5),
`availability` → `in_stock` (bool). Output saved to
`data/processed/books_clean.csv`.

**Design decisions**
- The raw CSV is read with `encoding="utf-8"` explicitly, matching how
  `scrape.py` writes it, to avoid decode mismatches.
- `clean_price()` strips currency symbols using a regex
  (`re.sub(r"[^\d.]", "", price)`) that removes everything except digits
  and the decimal point, rather than replacing one exact `£` character.
  This was necessary because an earlier encoding bug in `scrape.py`
  (now fixed) had already saved some raw prices with a corrupted symbol
  (`Â£` instead of `£`); a regex strip is robust to this and any similar
  encoding artifact, whereas an exact string match silently fails and
  returns no data for the whole column.
- **Numeric fields (`price_gbp`, `rating`) use median imputation** for
  rows that fail to parse. Median was chosen over mean because it's
  robust to outliers (e.g. one abnormally expensive book won't skew the
  fallback value), and imputing was chosen over dropping so a handful of
  malformed rows don't shrink the dataset below the 60-book minimum.
- **`in_stock` (boolean) has no numeric fallback**, so rows that fail to
  parse availability are dropped instead of guessed. Assigning a default
  True/False could quietly bias later stock-related analysis, so
  dropping is safer here than imputing.
- Rating words are mapped explicitly (`{"One": 1, ..., "Five": 5}`)
  rather than parsed positionally, to avoid silent errors if the site's
  wording changes.

**How to run**
```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\clean.py
```

**Output**
`data_pipeline/data/processed/books_clean.csv` — cleaned rows with typed
columns: `title`, `price_gbp`, `rating`, `in_stock`, `category`. Console
output reports how many rows needed imputation or were dropped.

## Stage 3 — Convert (`convert.py`)

**What it does**
Reads `data/processed/books_clean.csv` and adds a `price_inr` column,
converting each book's `price_gbp` using a fixed baseline rate. Output
saved to `data/processed/books_converted.csv`.

**Design decisions**
- Conversion rate is a **fixed, project-defined constant: 1 GBP = 105.50
  INR**. This is not a live/historical market rate — it's the required
  graded baseline for this assignment, so no API call or network lookup
  is used. The rate is hardcoded as `GBP_TO_INR_RATE` and stated here in
  the README as required.
- The assignment allows an *optional, ungraded* stretch of looking up a
  free currency API with explicit status-code handling and falling back
  to the fixed rate on failure. This was intentionally left out of the
  required submission, since it adds external dependency risk for zero
  additional marks — `price_inr` must be correct using only the fixed
  baseline regardless, so that's the only path implemented.
- `price_inr` is rounded to 2 decimal places to match standard currency
  precision.

**How to run**
```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\convert.py
```

**Output**
`data_pipeline/data/processed/books_converted.csv` — same as the cleaned
dataset, with an added `price_inr` column.

## Stage 4 — Store (`store.py`)
*(to be added)*

## Stage 5 — Query (`query.py`)
*(to be added)*