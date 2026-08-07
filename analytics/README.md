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
│   ├── 01_eda.ipynb                    # Part A: cleaning + EDA
│   ├── 02_modeling.ipynb               # Part B: modeling
│   └── titanic_survival_pipeline.joblib # saved complete pipeline
├── titanic.csv                          # offline fallback of the raw load
├── titanic_clean.csv                    # cleaned dataset for modeling
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
Loads `titanic_clean.csv` (already cleaned in Part A) as the starting point for modeling.

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

Training set class counts before SMOTE: `{0: 439, 1: 272}` (imbalanced).
After SMOTE: `{0: 439, 1: 439}` (perfectly balanced via synthetic
minority samples).

| Variant | Precision | Recall | F1 Score |
|---|---|---|---|
| (a) Baseline | 0.8136 | 0.7059 | 0.7559 |
| (b) class_weight=balanced | 0.7714 | **0.7941** | **0.7826** |
| (c) SMOTE (train only) | 0.7727 | 0.7500 | 0.7612 |

**Conclusion:** `class_weight='balanced'` worked best overall — it
achieved the highest recall (0.7941) and highest F1 score (0.7826) of
the three variants, meaning it catches more true survivors than either
the baseline or SMOTE, while still keeping a reasonable precision.
SMOTE improved recall over the baseline too (0.75 vs 0.71) but not as
much as class weighting, despite doing more work (generating synthetic
data) to get there. The baseline has the highest precision (0.8136) but
the lowest recall — it's more conservative about predicting survival,
which means it misses more actual survivors. Since correctly identifying
survivors (recall) is arguably the more important goal for this kind of
problem, `class_weight='balanced'` is the preferred strategy: it
achieves this without the added complexity and risk of data leakage
that comes with resampling techniques like SMOTE.

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

**Result:**

Best parameter combination: `{'max_depth': 5, 'max_features': 'sqrt', 'n_estimators': 300}`
Best cross-validation accuracy: **0.8242**
Out-of-bag (OOB) score of best estimator: **0.8284**

The OOB score (0.8284) closely tracks the cross-validation accuracy
(0.8242), which is a good sanity check — both estimate generalization
performance independently (OOB from unused bootstrap samples,
cross-validation from held-out folds), and their agreement suggests the
tuned Random Forest isn't overfitting to the training data.

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

**Result:**

| Metric | Value |
|---|---|
| MAE | 21.368 |
| RMSE | 42.421 |
| R² | 0.3255 |
| Adjusted R² | 0.2894 |

RMSE (42.4) is roughly double MAE (21.4) — a strong sign that a
relatively small number of predictions are very wrong, consistent with
`fare`'s heavy right-skew pulling large errors on the few expensive
tickets. R² of 0.33 means the model explains only about a third of the
variance in fare — the other numeric/encoded features (class, age,
family size, etc.) capture some of what drives fare, but far from all
of it, since a linear model can't fully capture the sharp jump between
fare tiers.

**Heteroscedasticity conclusion:** Yes, the residual plot shows clear
heteroscedasticity. Residuals stay small and tightly clustered near
zero for low predicted fares, then fan out into a wide, funnel-shaped
spread as predicted fare increases — the model's errors on expensive
1st-class tickets are far larger and more variable than its errors on
cheap 3rd-class tickets. This is expected given `fare`'s right-skewed
distribution (established in Task 3) and confirms that a plain linear
regression isn't fully appropriate for this target without further
transformation (e.g. predicting log(fare) instead of raw fare would
likely reduce this effect).

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

### Cell 15 — Best-Performing Complete Pipeline (Save & Reload)
Saves the best-performing model (Logistic Regression) together with
its full preprocessing (imputer + encoder + scaler) as **one combined
`Pipeline` object**, so the saved artifact works end-to-end on raw,
unprocessed new data — not just the bare classifier alone.

**Why the entire `Pipeline` is saved, not just the classifier:** if
only the bare model were saved, anyone using it later would need to
manually reproduce every preprocessing step (imputation, exact
encoding scheme, scaler parameters) themselves before predicting — easy
to get wrong or inconsistent with training. Saving the full pipeline
means `.predict()` on new raw data does everything correctly and
automatically inside one object.

**Why it's trained fresh on `titanic_clean.csv` reloaded from disk,
not on this notebook's already-encoded `df`:** the whole point is that
the pipeline's own `ColumnTransformer` does the encoding internally, so
it must be fit starting from genuinely raw category values (e.g.
`"female"`, not a pre-encoded number) — otherwise the saved pipeline
wouldn't actually work on true raw input.

**Why `OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)`:**
makes the pipeline robust to a category it never saw during training
(e.g. a user typo) — it encodes the unknown value as `-1` instead of
crashing, so a single bad input field doesn't break the whole pipeline.

**Result:** Full pipeline test accuracy: **0.8146**, closely matching
Logistic Regression's earlier standalone test accuracy (0.8258),
confirming the end-to-end pipeline performs consistently with the
manually-preprocessed version used earlier in this notebook. Reloading
the saved `.joblib` file and predicting on a fresh raw sample (e.g. a
1st-class woman, age 29, fare 100) correctly reproduces the same
prediction and probability as the freshly-trained pipeline, confirming
nothing was lost in the save/load process.