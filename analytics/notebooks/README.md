# Module 2 — Analytics (`/analytics`)

Zepto's analyst-to-data-scientist workflow in one pass: profile a dataset,
clean it defensibly, tell a visual story, then build a predictive-modeling
pipeline — all on the same cleaned data, loaded once.

**Dataset:** Titanic, loaded via `sns.load_dataset('titanic')` — exactly
once, in the very first cell of `01_eda.ipynb`. Immediately after loading,
the raw DataFrame is saved to `titanic.csv` as a committed offline
fallback, so grading can proceed via `pd.read_csv("titanic.csv")` even
without network access. Every subsequent step, in both notebooks, works
off that same load — no second `sns.load_dataset` call anywhere.

**Structure**
```
analytics/
├── notebooks/
│   ├── 01_eda.ipynb       # Part A: profiling, cleaning, EDA story
│   └── 02_modeling.ipynb  # Part B: modeling pipeline (to be added)
├── titanic.csv            # committed offline fallback (raw load)
├── data/
└── README.md
```

---

## `01_eda.ipynb` — Part A: Profiling, Cleaning, Data Story

### Cell 1 — Load dataset, save offline fallback, profile
Loads Titanic via `sns.load_dataset('titanic')` (the one and only network
call in the whole project), immediately saves it to `titanic.csv` before
any cleaning happens, then prints `df.shape`, `df.info()`, and
`df.describe()`.
**Why save before cleaning:** if any later cleaning step has a bug and
the notebook crashes, the raw data is still safely on disk — the fallback
represents the true one-time load, not a partially-processed version.

### Cell 2 — Missing value percentages
Computes `(missing count / total rows) * 100` per column, filters to only
columns that actually have missing values, and sorts descending.
Result: `deck` (77.2%), `age` (19.9%), `embarked` (0.22%), `embark_town`
(0.22%).

### Cell 3 — Unique values of `deck`
Prints `df["deck"].unique()` to inspect what values exist before deciding
how to handle the column (mostly `NaN`, plus deck letters A–G).

### Cell 4 — Drop `deck` column
At ~77% missing, there isn't enough real data left to impute reliably —
filling three-quarters of a column would be mostly fabricated values
rather than genuine signal. Dropped entirely rather than imputed.

### Cell 5 — Group-based median imputation for `age`
`age` is ~20% missing — enough real data to base an imputation on,
unlike `deck`. Instead of filling with one flat overall median, the
median is computed **per `pclass` + `sex` group** (6 groups total) and
merged back onto each row, since typical age varies meaningfully by
class and gender on this dataset (e.g. 1st-class passengers skew older
than 3rd-class). Implemented via `groupby().median()` + `merge()` +
`fillna()`, deliberately avoiding `apply`/lambda/custom function
definitions in favor of vectorized pandas operations.

### Cell 6 — Unique values of `embarked` and `embark_town`
Prints both columns' unique values to confirm they represent the same
information at different levels of detail: `embarked` is a 1-letter
port code (`S`/`C`/`Q`), `embark_town` is the full town name
(`Southampton`/`Cherbourg`/`Queenstown`).

### Cell 7 — Drop `embark_town` column
Since `embark_town`'s value is fully derivable from `embarked` (first
letter always matches), keeping both is redundant duplication of the
same signal. `embarked` is kept since it's already in a compact,
encoding-ready form for modeling later.

### Cell 8 — Drop rows with missing `embarked`
Only 0.22% of rows (2 total) have a missing `embarked` value. At this
scale, dropping is simpler and safer than imputing a mode value —
unlike `age`, there's no meaningful class/gender-based pattern worth
preserving for just 2 rows, and the loss to the dataset is negligible.

### Cell 9 — Drop `alive` column
`alive` (`"yes"`/`"no"`) and `survived` (`1`/`0`) encode identical
information in string vs. numeric form. `survived` is kept since it's
already in the numeric form needed as the target variable for modeling.

### Cell 10 — Drop `adult_male` column
`adult_male` (`True`/`False`) is a narrower version of the signal
already captured more completely by `who` (`man`/`woman`/`child`).
Note: `who` and `adult_male` are **not** pure duplicates of `sex` —
both also encode child-status (age < 18) on top of sex, so they aren't
redundant with `sex` alone. Between the two, `who` was kept (it retains
the distinct `child` category) and `adult_male` was dropped as the
narrower, more redundant of the pair.

### Cell 11 — Drop `class` column
`class` (`"First"`/`"Second"`/`"Third"`) and `pclass` (`1`/`2`/`3`)
encode identical information in string vs. numeric form. `pclass` is
kept since it's already numeric and ready for modeling.

---

## `02_modeling.ipynb` — Part B: Modeling pipeline
*(to be added)*