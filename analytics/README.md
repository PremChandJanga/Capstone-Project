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

## Part B — `02_modeling.ipynb`

Reads the cleaned, encoded dataset saved by `01_eda.ipynb`
(`titanic_clean.csv`) and continues into the modeling pipeline. No
second `sns.load_dataset('titanic')` call — everything here builds on
the one load from Part A.

### Cell 1 — Load cleaned dataset
Loads `titanic_clean.csv` (already cleaned + encoded to numeric in Part
A) as the starting point for modeling.

### Cell 2 — Stratified train/test split
Splits data into train (80%) and test (20%) sets using
`train_test_split(..., stratify=y)`, with `survived` as the
classification target.

**Why a stratified split is necessary here:** `survived` is an
imbalanced target — roughly 38% survived vs. 62% did not (seen in
Task 1's profiling). A plain random split risks landing on a different
survival rate in train vs. test purely by chance, especially on a
dataset this size (~891 rows, further reduced by the split). That
mismatch would mean the model trains on one class balance but gets
evaluated on a different one, making test performance less reliable to
interpret. `stratify=y` forces train and test to preserve the same
survival rate as the full dataset.

**Why `random_state=42`:** makes the split reproducible — same rows in
train/test every time the cell runs, instead of a different random
split on each run.

### Cells 5–6 — Train three classifiers + render Decision Tree
Trains **Logistic Regression**, **Decision Tree**, and **Random
Forest** on the same processed train split (`X_train_processed`,
`y_train`). The Decision Tree is additionally rendered with
`plot_tree`, labeling feature names and class names
(`"Did Not Survive"` / `"Survived"`) for readability.

- `max_iter=1000` on Logistic Regression: the default (100) can fail to
  converge on this dataset/feature set; raising it just gives the
  optimizer more room to settle, without changing its approach.
- `random_state=42` on all three: keeps each model's internal
  randomness (tree splits, forest bootstrap sampling) reproducible.

### Cells 7–9 — Evaluate all three models (confusion matrix, metrics, ROC/AUC)
Computes accuracy, precision, recall, F1, and AUC for each model on the
test set, presented as one comparison table; confusion matrices shown
side by side (3 subplots); ROC curves overlaid on a single shared plot
for direct visual comparison.

**Why AUC uses `predict_proba` instead of `predict`:** AUC measures
ranking quality across *all* possible thresholds, not just the default
0.5 cutoff that `.predict()` applies — this requires the model's raw
probability scores.

**Result — AUC comparison:**

| Model | AUC |
|---|---|
| Logistic Regression | **0.87** |
| Random Forest | 0.82 |
| Decision Tree | 0.77 |

**Interpretation:** Logistic Regression has the highest AUC and its ROC
curve sits closest to the top-left corner across most of the plot,
meaning it's best at ranking survivors above non-survivors regardless
of threshold. This doesn't automatically make it "the best model" in
every sense — accuracy/precision/recall at the default threshold could
tell a different story for a specific use case — but specifically for
ranking quality (what AUC measures), it's the clear winner of the
three.

*(Full accuracy/precision/recall/F1 table to be filled in from actual
run output.)*

### Cells 10–14 — Imbalance Handling Comparison
Reports the `survived`/not-survived class balance, then retrains
Logistic Regression three ways to compare strategies for handling that
imbalance.

**Why Logistic Regression specifically:** the task allows any one of
the three models; Logistic Regression is used here since it already
showed the strongest AUC in the earlier model comparison, making it the
most relevant model to fine-tune further.

- **(a) Baseline** — no imbalance handling at all. Trained on the
  original imbalanced training data as-is; every other variant is
  compared against this.
- **(b) `class_weight='balanced'`** — doesn't touch the data. Instead
  changes the *loss function* so misclassifying the minority class
  (survivors) is penalized more heavily during training, based on
  class frequency.
- **(c) SMOTE oversampling** — generates *synthetic* minority-class
  rows by interpolating between real minority examples, rather than
  duplicating existing rows.

**Why SMOTE is applied only to the training fold
(`smote.fit_resample(X_train_processed, y_train)`), never to test
data:** if applied before the split, or directly to test data,
synthetic points generated near real test rows could leak test-set
information into training — inflating apparent performance. Restricting
it strictly to the training fold keeps the test set 100% real and
untouched, consistent with the fit-on-train-only rule from Task 8.

**Result:**

*(Class balance and precision/recall/F1 comparison table to be filled
in from actual run output, along with a short written conclusion on
which strategy worked best and why.)*

### Cell 15 — Hyperparameter Tuning (GridSearchCV on Random Forest)
Runs `GridSearchCV` over Random Forest's `n_estimators`, `max_depth`,
and `max_features`, reporting the best parameter combination and its
out-of-bag (OOB) score.

**Why `oob_score=True` is passed at construction
(`RandomForestClassifier(oob_score=True, ...)`), not set afterward:**
OOB scoring happens *during* training — each tree is evaluated on the
portion of data its own bootstrap sample excluded. This tracking is
only set up if the flag is enabled before `.fit()` runs; setting it
after fitting has no effect.

**Why the OOB score is read from `grid_search.best_estimator_`, not the
base estimator:** `GridSearchCV` internally clones the base estimator
for every parameter combination it tests, but `best_estimator_` is the
one specific model — built with the winning parameters — that gets
refit on the full training set afterward. That final refit is what
produces a meaningful `oob_score_`.

**Why `n_jobs=-1`:** uses all available CPU cores, since the grid tests
`3 × 4 × 2 = 24` parameter combinations × 5 CV folds = 120 model fits.

*(Best parameter combination and OOB score to be filled in from actual
run output.)*

### Cells 16–18 — Regression Side-Task: Predicting `fare`
Using the same dataset, predicts `fare` from the other available
features with a multivariate linear regression — a separate side-task
from the survival classification above.

**Why a separate train/test split (`X_reg_train`/`X_reg_test`) instead
of reusing the earlier `X_train`/`X_test`:** the target changes from
`survived` to `fare`, and `survived` itself becomes a predictor here —
this is a genuinely different modeling problem, so it gets its own
split rather than reusing the classification task's split.

**Metrics reported:**
- **MAE** — average error in the same units as fare (directly
  interpretable: "predictions are off by about £X on average")
- **RMSE** — penalizes large errors more heavily than MAE; expected to
  be noticeably larger than MAE here given fare's right-skew (a few
  very expensive tickets are harder to predict accurately, and RMSE
  reflects that more than MAE does)
- **R²** — proportion of fare's variance explained by the model
- **Adjusted R²** — same as R², but penalized for the number of
  predictors used, so it doesn't automatically reward adding more
  features

**Residual plot:** plots predicted fare (x-axis) against residuals
(actual − predicted, y-axis), with a reference line at 0.
**Why this checks for heteroscedasticity:** if residuals fan out into a
funnel/cone shape — tight near low predicted fares, wide near high
predicted fares — rather than a consistent random band around zero
across the whole range, that's heteroscedasticity (non-random,
uneven spread of errors). Given `fare`'s heavy right-skew (established
back in Task 3's univariate analysis), this pattern is expected: errors
on a handful of very expensive tickets are likely much larger and more
variable than errors on the many cheap tickets.

*(Actual MAE/RMSE/R²/Adjusted R² values, residual plot description, and
written heteroscedasticity conclusion to be filled in from run output.)*

### Cell 19 — Final Model Comparison Table
Presents the three classifiers' metrics (accuracy, precision, recall,
F1, AUC) and the regression model's metrics (MAE, RMSE, R², Adjusted
R²) as **two distinct tables**, not merged into shared columns.

**Why classification and regression metrics are kept as separate
tables rather than one combined table:** classification metrics
(accuracy, precision, recall, F1, AUC) are bounded 0–1 scores where
higher is always better, while regression metrics (MAE, RMSE, R²) are
on entirely different scales — MAE/RMSE are in fare's own units and
lower is better, R² can even go negative. Presenting them under shared
columns would visually imply they're comparable numbers, which they
are not. Two clearly labeled tables — one per model type — satisfies
"side by side" without misrepresenting what each number measures.

**Actual results:**

Classification Models — Predicting Survival

| Model | Accuracy | Precision | Recall | F1 Score | AUC |
|---|---|---|---|---|---|
| Logistic Regression | **0.8258** | **0.8136** | 0.7059 | **0.7559** | **0.8670** |
| Decision Tree | 0.7865 | 0.7206 | **0.7206** | 0.7206 | 0.7691 |
| Random Forest | 0.7921 | 0.7385 | 0.7059 | 0.7218 | 0.8205 |

Regression Model — Predicting Fare

| Model | MAE | RMSE | R² | Adjusted R² |
|---|---|---|---|---|
| Linear Regression (fare) | 21.368 | 42.421 | 0.3255 | 0.2894 |

**Final Recommendation:**
Logistic Regression is the recommended model for deployment. It
achieved the highest accuracy (0.8258), precision (0.8136), F1 score
(0.7559), and AUC (0.8670) of the three classifiers, outperforming both
Random Forest and Decision Tree on nearly every metric. Its recall
(0.7059) is only marginally behind Decision Tree's (0.7206), a
negligible trade-off given Logistic Regression's clear advantage
everywhere else — notably its precision, which is roughly 7–9 points
higher than the other two, meaning far fewer false-positive survival
predictions. Beyond raw performance, Logistic Regression is also
simpler to interpret and less prone to overfitting than a single
Decision Tree, making it a more stable and explainable choice for a
production setting. For these reasons — consistently strongest metrics
plus practical interpretability — Logistic Regression is the model I
would deploy.

### Cell 3 — Encode categorical columns to numeric
Converts remaining category columns to numeric, applied **after** the
train/test split (not in `01_eda.ipynb`), so encoding is scoped to the
modeling pipeline rather than baked into the shared cleaned dataset.

- **`sex`** (2 values) → mapped directly to `0`/`1`
- **`embarked`** (S/C/Q, unordered) → one-hot encoded
- **`who`** (man/woman/child, unordered) → one-hot encoded
- **`alone`** (already boolean) → converted to `0`/`1`
- **`pclass`** left as-is — already numeric and genuinely ordinal

**Why one-hot instead of simple number mapping for `embarked`/`who`:**
mapping categories to arbitrary numbers (e.g. S=1, C=2, Q=3) would
falsely imply a ranking between them that doesn't exist.

**Why encoding happens here, after the split, rather than in
`01_eda.ipynb` before it:** keeps `titanic_clean.csv` as a
general-purpose cleaned dataset (still human-readable categories),
with encoding scoped specifically to this modeling pipeline. It also
avoids a subtle risk: one-hot encoding the *full* dataset before
splitting is usually fine here since all categories appear in both
splits, but doing it after split-time in the pipeline is the safer
default habit, consistent with how scaling is handled in Task 6/Task 8.