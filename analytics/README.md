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

### Cells 12–13 — Histograms for `age` and `fare`
Plots the distribution shape of each column separately.

**Data story — `age`:** The age distribution is roughly unimodal and
centered in the young-to-middle-adult range, with the majority of
passengers falling between about 20 and 50 years old. There's a smaller
secondary cluster of children and infants at the low end, and the
distribution tapers off gradually into older ages, with relatively few
passengers above 60. This is a fairly typical bell-shaped spread for a
passenger population that includes some traveling families but skews
toward working-age adults.

**Data story — `fare`:** The fare distribution is heavily right-skewed
— most passengers paid relatively low fares (concentrated roughly in
the £0–50 range), reflecting that the majority traveled 3rd class,
which was the cheapest. A long tail stretches out toward much higher
fares (£200+), driven by a smaller number of 1st-class passengers who
paid significantly more. This shape — a tall cluster near zero with a
thin tail extending right — is the classic signature of a right-skewed
distribution, and it foreshadows why `fare`'s mean will likely sit
noticeably above its median once those are computed.

### Cells 14–15 — Box plots for `age` and `fare`
Visualizes each column's median, quartile spread, and flags outliers as
individual points beyond the whiskers.

**Data story — `age`:** The `age` box plot shows a relatively compact,
fairly symmetric box centered around the late-20s median, with whiskers
extending to cover most of the passenger age range. Only a small number
of points appear beyond the upper whisker — a few older passengers in
their 60s–80s — and the box itself isn't heavily skewed in either
direction. This lines up with the histogram: age is a well-behaved,
roughly bell-shaped distribution with just a handful of genuine
outliers at the older end.

**Data story — `fare`:** The `fare` box plot tells a very different
story — a tightly compressed box sitting near the bottom of the chart
(reflecting how cheap most 3rd-class tickets were), with a long run of
individual dots stretching far above the upper whisker. Each of those
dots is a passenger who paid a fare well beyond what's typical, up to
the most expensive 1st-class tickets. Visually, this is a textbook
right-skewed distribution: a small, low-value box with a substantial
number of high-value outliers pulling the range upward, consistent with
what the fare histogram already showed.

### Cells 16–17 — Outlier counts for `age` and `fare` (IQR rule)
Applies the standard IQR (interquartile range) rule to count outliers
in each column separately.

**Why the IQR rule instead of, e.g., a fixed cutoff or z-score method:**
The IQR rule adapts to each column's own spread rather than using an
arbitrary fixed threshold (like "age > 70"), and unlike a z-score
approach, it doesn't assume the data is normally distributed — which
matters here since `fare` is visibly right-skewed, not bell-shaped.
`Q1 - 1.5*IQR` / `Q3 + 1.5*IQR` is the conventional, widely-used
boundary for flagging a value as unusual relative to the middle 50% of
that column's own data.

**Why bounds/outlier counts are computed separately per column, not
together:** `age` and `fare` have completely different scales and
distributions (age is roughly symmetric, fare is heavily right-skewed),
so a shared threshold would be meaningless — each column needs its own
Q1, Q3, and IQR computed independently before the rule is applied.

*(Outlier counts to be filled in from actual run output.)*

### `02_modeling.ipynb` — Part B: Modeling pipeline
*(to be added)*