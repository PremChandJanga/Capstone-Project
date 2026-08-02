# Module 2 — Analytics (`/analytics`)

Zepto's analyst-to-data-scientist workflow: profile the Titanic dataset,
clean it, explore it visually, then build a modeling pipeline — all on
one cleaned dataset, loaded once.

**Dataset load:** `sns.load_dataset('titanic')` is called **once**, in
Cell 1 of `01_eda.ipynb`. Immediately saved as `titanic.csv` so grading
can run offline via `pd.read_csv` if needed. Nothing after Cell 1 loads
from the network again.

```
analytics/
├── notebooks/
│   ├── 01_eda.ipynb        # Part A: cleaning + EDA
│   ├── 02_modeling.ipynb   # Part B: modeling (to be added)
│   ├── titanic.csv          # offline fallback of the raw load
│   └── titanic_clean.csv    # cleaned + encoded dataset for modeling
└── README.md
```

---

## Part A — Cleaning (Cells 1–11)

| Cell | Action | Why |
|---|---|---|
| 1 | Load dataset, save `titanic.csv`, profile (`shape`, `info`, `describe`) | Save happens before any cleaning, so raw data is safe even if later cells fail |
| 2 | % missing per column | `deck` 77%, `age` 20%, `embarked`/`embark_town` 0.2% |
| 3 | Unique values of `deck` | Inspect before deciding how to handle it |
| 4 | Drop `deck` | 77% missing — not enough real data to impute reliably |
| 5 | Impute `age` with median **per `pclass`+`sex` group** | Typical age varies a lot by class/gender; better than one flat median. Done via `groupby`+`merge`+`fillna` (no lambda/functions) |
| 6 | Unique values of `embarked`/`embark_town` | Confirm they duplicate the same info (code vs. full name) |
| 7 | Drop `embark_town` | Fully redundant with `embarked` |
| 8 | Drop rows missing `embarked` | Only 2 rows (0.2%) — safe to drop, not worth imputing |
| 9 | Drop `alive` | Redundant with `survived` (same info, string vs. numeric) |
| 10 | Drop `adult_male` | Narrower version of `who` (which also has `child`, so it's kept) |
| 11 | Drop `class` | Redundant with `pclass` (string vs. numeric) |

---

## Part A — Univariate Analysis: `age` & `fare` (Cells 12–19)

- **Cells 12–13 (histograms):** `age` is roughly bell-shaped, centered
  20–50. `fare` is right-skewed — most fares are low (3rd class),
  with a long tail of expensive 1st-class tickets.
- **Cells 14–15 (box plots):** `age` box is compact with few outliers.
  `fare` box is small and low, with many outlier dots above — visually
  confirms the right-skew.
- **Cells 16–17 (IQR outlier count):** Uses `Q1 - 1.5×IQR` /
  `Q3 + 1.5×IQR` to flag outliers per column, computed separately since
  `age` and `fare` have very different scales/shapes.
  *(fill in actual counts once run)*
- **Cells 18–19 (mean/median/mode, skew):** For `fare`: mean > median >
  mode confirms **right-skew** — a few expensive fares pull the mean up
  above the median/mode.
  *(fill in actual values once run)*

---

## Part A — Bivariate Analysis (Cells 20–25)

- **Cells 20–22 (survival rate via boolean masking):** by `sex`, by
  `pclass`, and by both together (`&` combined masks). Expect: females
  and 1st class survive at higher rates, compounding when combined.
  *(fill in actual rates once run)*
- **Cell 23 (correlation matrix):** Uses exactly `survived`, `pclass`,
  `age`, `sibsp`, `parch`, `fare`. `adult_male`/`alone` excluded — both
  are derived flags (computable from other columns), not independent data.
- **Cell 24 (heatmap):** Visualizes the matrix with `sns.heatmap`.
- **Cell 25 (top 2 correlations):** Ranks off-diagonal pairs by
  **absolute value** (negative correlations count too), filtering out
  self-correlations and duplicate pairs.
  *(fill in actual top 2 pairs once run)*

---

## Part A — Multivariate Data Story (Cells 26–29)

Four charts building one argument: **survival depended on sex, class,
age, and family size together, not any one factor alone.**

1. **Bar chart** — survival rate by class × sex
2. **Box plot** — age distribution, survived vs. not
3. **Scatter plot** — age vs. fare, colored by survival
4. **Heatmap** — survival rate by class × family size
   (`family_size = sibsp + parch + 1`, created just for this chart)

*(Add a 2–4 sentence interpretation under each chart once run, based on
what the actual chart shows.)*

---

## Part A — EDA Sanity Check: Z-Score Standardization (Cells 30–31)

Standardizes `age`/`fare` manually (`z = (x - mean) / std`) into new
columns (`age_zscore`, `fare_zscore`) — **originals kept untouched**.

**Important:** this is throwaway — it does *not* feed into the modeling
pipeline. Task 8's pipeline does its own scaling, fit only on training
data, to avoid data leakage. This is just to show the transformation
works (after: mean ≈ 0, std ≈ 1).

*(Fill in actual before/after mean/std once run.)*

---

## Categorical Encoding (Cells 32–33)

To prime the data for model training, all category columns were
converted into numerical columns, since models require numeric input.

- **`sex`** (2 values) → mapped directly to `0`/`1`
- **`embarked`** (S/C/Q, unordered) → one-hot encoded into
  `embarked_S`, `embarked_C`, `embarked_Q`
- **`who`** (man/woman/child, unordered) → one-hot encoded into
  `who_man`, `who_woman`, `who_child`
- **`alone`** (already boolean) → converted to `0`/`1` with `.astype(int)`
- **`pclass`** left as-is — already numeric and genuinely ordinal
  (1st > 2nd > 3rd), so it doesn't need one-hot encoding like the
  unordered categories above

**Why one-hot instead of simple number mapping for `embarked`/`who`:**
mapping categories to arbitrary numbers (e.g. S=1, C=2, Q=3) would
falsely imply a ranking between them. One-hot encoding avoids that by
giving each category its own independent 0/1 column.

The updated dataset (all columns numeric) is saved back to
`titanic_clean.csv` for use in `02_modeling.ipynb`.

## Part B — `02_modeling.ipynb`
*(to be added)*