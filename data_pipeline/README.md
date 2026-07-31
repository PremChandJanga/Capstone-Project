# Module 1 — Data Pipeline (`/data_pipeline`)

This module plays the data-engineering role for Zepto's analytics guild:
scrape catalog-style data from a public site, clean it, convert currency,
load it into a normalized relational database, and query it with both SQL
and pandas.

**Pipeline stages:** `scrape → clean → convert → store → query`

**Why 5 separate scripts instead of one script:**
A single monolithic script would be harder to debug (a failure anywhere
would be indistinguishable from a failure everywhere) and harder to
re-run selectively (e.g. re-scraping shouldn't force re-cleaning if
cleaning logic didn't change). Splitting by stage also mirrors how a
real ETL pipeline is structured in production — each stage has one job,
reads a defined input, and writes a defined output.

**Why intermediate CSV files between stages instead of passing data
directly in memory:**
Writing each stage's output to disk (`raw → clean → converted`) makes
every stage independently inspectable and re-runnable without re-running
earlier stages. If Stage 4 (store) had a bug, we could fix and re-run
just that script against the existing `books_converted.csv`, instead of
re-scraping the website again.

---

## Stage 1 — Scrape (`scrape.py`)

**What it does**
Scrapes book listings from three categories — `Nonfiction`, `Romance`,
`Sequential Art` — from books.toscrape.com. For each book it captures:
`title`, `price`, `star_rating`, `availability`, `category`. Saves raw,
unmodified data to `data/raw/books_raw.csv`.

**Why `requests` + `BeautifulSoup` instead of Scrapy or Selenium**
The site is static HTML with no JavaScript rendering and no login wall,
so a full scraping framework (Scrapy) or browser automation (Selenium)
would be unnecessary overhead. `requests` fetches the page and
`BeautifulSoup` parses it — the minimum toolset that does the job,
which also keeps the dependency list small (a stated goal since no
paid/complex services are needed anywhere in this project).

**Why category URLs are looked up dynamically instead of hardcoded**
books.toscrape.com assigns each category a numeric ID in its URL (e.g.
`romance_8`) that isn't predictable from the category name alone.
Hardcoding `.../romance_8/index.html` would work today but breaks the
moment the site regenerates its catalog with different IDs. Reading the
category link straight from the homepage sidebar means the script keeps
working regardless of what ID the site assigns.

**Why pagination is followed via a "next page" check instead of a fixed
page-count loop**
The three categories have different numbers of books, so a fixed
`for page in range(1, 5)` loop would either miss books (too few pages)
or throw errors requesting pages that don't exist (too many). Checking
for a `li.next` link and stopping when it's absent adapts automatically
to however many pages each category actually has.

**Why no cleaning/type conversion happens in this script**
Fields are stored exactly as scraped (e.g. price as `"£51.77"`, rating
as the word `"Three"`). Mixing scraping and cleaning in one script means
a change to cleaning logic would require re-scraping the website to
test it. Keeping scrape "dumb" (collect only) and pushing all
transformation to Stage 2 means cleaning logic can be changed and
re-tested against the same saved raw file, without hitting the website
again.

**Why `resp.encoding = "utf-8"` is set explicitly on every request**
`requests` guesses a page's text encoding from HTTP headers when the
server doesn't declare it precisely, and on this site it sometimes
guessed `ISO-8859-1` instead of the actual `UTF-8` encoding. Left
unfixed, this silently corrupted the `£` currency symbol into garbage
characters (e.g. `Â£`) before the data was even written to CSV — a bug
that surfaced during testing (see Stage 2 notes below). Setting the
encoding explicitly removes the ambiguity at the source, rather than
trying to repair corrupted text later.

**Why a `time.sleep(0.5)` delay between page requests**
Firing requests as fast as possible is unnecessary here and is bad
practice against any real server, scraping-practice site or not. A half
second delay is negligible for total runtime but keeps request
frequency reasonable.

**Why CSV output instead of writing directly to the database**
Stage 1's only job is to get the data off the website reliably. Writing
straight to SQLite here would couple the scraping stage to the database
schema, so any schema change would force a re-scrape. A plain CSV is a
stable, inspectable checkpoint that later stages build on independently.

**How to run**
```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\scrape.py
```

**Output**
`data_pipeline/data/raw/books_raw.csv` — ≥60 raw rows across the 3
required categories (220 rows in this run).

---

## Stage 2 — Clean (`clean.py`)

**What it does**
Reads `data/raw/books_raw.csv` and converts each raw field into a proper
type: `price` → `price_gbp` (float), `star_rating` → `rating` (int 1–5),
`availability` → `in_stock` (bool). Saves to `data/processed/books_clean.csv`.

**Why `encoding="utf-8"` is specified on the CSV read**
This matches how `scrape.py` writes the file. Without an explicit match,
`pandas.read_csv` can fall back to a system-default encoding (e.g.
`cp1252` on Windows), which would misinterpret non-ASCII bytes like `£`
all over again on the read side, even after fixing the write side.

**Why `clean_price()` uses a regex strip (`re.sub(r"[^\d.]", "", price)`)
instead of `price.replace("£", "")`**
During testing, the raw CSV was found to contain a corrupted currency
symbol (`Â£` instead of `£`) from an earlier encoding bug in
`scrape.py`. An exact-match `.replace("£", "")` silently failed against
`Â£` — it didn't error, it just didn't remove anything, so `float()`
then failed on every row and the entire `price_gbp` column came back
empty with no obvious error message. A regex that strips *everything
except digits and the decimal point* is agnostic to whatever symbol or
encoding artifact precedes the number, so it's robust to this class of
bug regardless of its exact cause — a stricter but more fragile match
would only mask the symptom, not the underlying risk of it recurring.

**Why star ratings are mapped with an explicit dictionary
(`{"One": 1, ..., "Five": 5}`) instead of parsed positionally**
An explicit lookup table fails loudly (returns `None`, which is then
handled) if the site ever used unexpected wording, rather than silently
producing a wrong number from a positional guess (e.g. assuming
word-length correlates with rating value, which it doesn't).

**Why numeric fields (`price_gbp`, `rating`) use median imputation for
rows that fail to parse, instead of the mean or dropping the row**
- **Median over mean:** median is robust to outliers — a single
  unusually expensive book wouldn't drag the fallback value away from
  what's typical, the way an average could.
- **Imputing over dropping:** the assignment requires a documented,
  justified choice, and dropping rows for a handful of malformed values
  risks losing otherwise-valid data (title, category, stock status are
  still fine even if price failed to parse) and could push the dataset
  under the 60-book minimum if enough rows failed.

**Why `in_stock` (boolean) rows are dropped instead of imputed**
Unlike price or rating, there's no meaningful "average" for a boolean —
imputing would mean arbitrarily guessing True or False for a row, which
could quietly bias any later stock-related analysis (e.g. inflating
`in_stock` counts). Dropping the row is more honest than fabricating a
stock status. In practice this path wasn't needed, since `availability`
parsed cleanly for every row in this run.

**How to run**
```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\clean.py
```

**Output**
`data_pipeline/data/processed/books_clean.csv` — cleaned, typed columns:
`title`, `price_gbp`, `rating`, `in_stock`, `category`.

---

## Stage 3 — Convert (`convert.py`)

**What it does**
Reads `data/processed/books_clean.csv` and adds a `price_inr` column,
converting `price_gbp` using a fixed baseline rate. Saves to
`data/processed/books_converted.csv`.

**Why a hardcoded fixed rate (1 GBP = 105.50 INR) instead of a live
currency API**
The assignment explicitly defines this as the required, graded baseline
— an artificial, project-defined constant with no date reference, not a
live market rate. Beyond compliance, it's also the more testable choice
for the fixed-rate part of the task: a hardcoded constant produces
identical, reproducible output every run, whereas a live API rate would
change daily and make `price_inr` a moving target that can't be
graded deterministically.

**Why the optional API-based stretch (mentioned in the task) was not
implemented**
The task states this is *ungraded* and explicitly must not affect the
required submission — `price_inr` has to be correct using only the
fixed baseline regardless of whether the stretch is attempted. Adding
an external API call here would introduce a network dependency and
failure path (timeouts, rate limits, API changes) for zero additional
marks, so it was left out to keep this stage simple and fully reliable.

**Why `price_inr` is rounded to 2 decimal places**
Matches standard currency precision (paise-level for INR) and avoids
long floating-point artifacts (e.g. `5516.599999999999`) appearing in
the stored data and later query outputs.

**How to run**
```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\convert.py
```

**Output**
`data_pipeline/data/processed/books_converted.csv` — same as cleaned
data, plus `price_inr`.

---

## Stage 4 — Store (`store.py`)

**What it does**
Loads `books_converted.csv` into a normalized SQLite database with two
tables — `categories` and `books` — linked by a primary/foreign key
relationship, plus three SQL views for convenience.

**Why two tables (`categories`, `books`) instead of one table per
category**
The task requires a normalized schema, and normalization specifically
means *not* duplicating structure or data for repeating groups.
Splitting the data into three separate physical tables (one per
category) would mean: (a) the same `books` columns defined three times
instead of once, (b) adding a 4th category later would require creating
an entirely new table rather than inserting a row, and (c) queries that
compare across categories (e.g. "cheapest book in each category") would
need to combine results from separate tables instead of a simple
`GROUP BY`. Storing all books in one table with a `category_id` foreign
key avoids all three problems and is exactly the two-table PK/FK
structure the task specifies.

**Why raw `sqlite3` + `cursor.execute()` instead of
`pandas.DataFrame.to_sql()`**
`to_sql()` is faster to write but gives limited control over table
constraints — expressing a `PRIMARY KEY` / `REFERENCES` foreign-key
relationship (the actual normalized structure required here) needs an
explicit `CREATE TABLE` statement, since `to_sql()` mainly infers a flat
schema from the DataFrame's dtypes and doesn't set up relational
constraints between tables on its own.

**Why `DROP TABLE IF EXISTS` runs before creating tables**
Makes the script idempotent — safe to re-run after a code change without
manually deleting the old database file first, and without ending up
with duplicate rows from running it twice.

**Why category IDs are generated manually (`enumerate` over unique
categories) instead of using pandas' index**
The category ID needs to be a small, stable integer that's reused
consistently as the foreign key on every one of that category's books.
Generating one ID per *unique* category name and mapping it into every
matching book row is what actually creates the relational link;
pandas' row index would instead assign a different number per *row*,
which wouldn't create a valid categories-to-books relationship at all.

**Why per-category SQL views instead of per-category tables**
This was the direct fix for wanting to see each category "separately"
without violating normalization: a `VIEW` is a saved, named query — it
doesn't store duplicate data, it just runs its underlying `SELECT`
against the real `books`/`categories` tables whenever queried. This
gives category-level visualization on demand while the actual stored
schema stays as the required two normalized tables.

**How to run**
```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\store.py
```

**Output**
`data_pipeline/db/books.db` — `categories` (3 rows), `books` (220 rows),
plus 3 views (`view_sequential_art`, `view_romance`, `view_nonfiction`).

---

## Stage 5 — Query (`query.py`)

**What it does**
Runs 5 SQL queries against the database covering every clause the task
requires, plus a side-by-side comparison of `pd.read_sql` (SQL join)
against `pd.merge` (in-memory pandas join) to confirm both approaches
produce identical results.

| Query | Clauses demonstrated |
|---|---|
| 1 | `SELECT` / `WHERE` — in-stock books over 2000 INR |
| 2 | `ORDER BY` / `LIMIT` — top 10 most expensive books |
| 3 | `DISTINCT` — all category names |
| 4 | `WHERE ... BETWEEN` — books rated 3 to 5 stars |
| 5 | `JOIN` + `ORDER BY` + `LIMIT` — top 10 highest-rated Romance books |

**Why these 5 specific queries instead of others**
Each was chosen to isolate one required clause as clearly as possible
(rather than one dense query trying to cover everything at once), so
it's obvious from reading the SQL which clause satisfies which
requirement — more useful for grading and for anyone reading the code
than a single query using every clause at once, which would obscure
which part does what.

**Why Query 5 combines JOIN with ORDER BY and LIMIT rather than being a
plain, unfiltered JOIN**
A bare `JOIN` with no filtering would return all 220 rows, which doesn't
demonstrate anything beyond "the relationship works." Filtering to one
category, ordering by rating, and limiting to 10 turns it into a
genuinely useful query (matching the task's own example: "list the 10
highest-rated books per category") while still exercising the JOIN.

**Why `books.book_id ASC` is added as a secondary sort key in Query 5**
Several Romance books share the same top rating. SQLite and pandas
don't necessarily break ties in the same order by default, so without a
secondary, deterministic sort key, `pd.read_sql` (SQL-side sort) and
`pd.merge` (pandas-side sort) could return the same 10 rows but in a
different order — which would make the automated equality check between
them report `False` even though the actual result sets matched. Adding
`book_id ASC` as a tiebreaker, on both the SQL query and the equivalent
`sort_values()` call in pandas, makes the ordering fully deterministic
so the two approaches can be compared exactly.

**Why the JOIN is reproduced with `pd.merge` on `category_id` rather
than `category_name`**
`category_id` is the actual foreign key relationship in the schema —
joining on it mirrors exactly what the SQL `JOIN ... ON
books.category_id = categories.category_id` does. Joining on
`category_name` instead would still work here since names happen to be
unique, but it wouldn't be testing the same relationship the schema
was built around, and would be fragile if two categories ever shared a
similar name.

**How to run**
```powershell
cd "D:\Projects\Capstone project"
python data_pipeline\query.py
```

**Output**
Terminal output shows all 5 queries with their SQL text and result
tables, followed by the `pd.merge` reproduction of Query 5 and a final
`True`/`False` check confirming both approaches match. (Full terminal
output pasted below.)

### Executed query output

```
<< PASTE FULL TERMINAL OUTPUT FROM query.py HERE >>
```