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

### Cell 18 — Mean, median, mode for `fare`
Computes the three standard measures of central tendency for `fare`:
- **Mean** — sum of all fares divided by passenger count. Sensitive to
  extreme values, since a handful of very expensive 1st-class tickets
  can pull it noticeably higher than what most passengers actually paid.
- **Median** — the middle fare once all values are sorted. Not affected
  by how extreme the highest/lowest values are, only their sorted
  position, making it a better read on the "typical" fare.
- **Mode** — the single most frequently occurring exact fare value.
  `.mode()` returns a list (in case multiple values tie for most
  common), so the first entry is taken.

*(Actual mean/median/mode values to be filled in from run output.)*

### Cell 19 — Determining skewness from mean/median/mode
Compares the three values computed in Cell 18 to determine the shape of
`fare`'s distribution, using the standard rule of thumb:
- `mean > median > mode` → **right-skewed** (long tail toward high
  values) — the mean is pulled upward by a small number of high fares
- `mean < median < mode` → **left-skewed** (long tail toward low
  values) — the mean is pulled downward by a small number of low fares
- All three roughly equal → **symmetric**, no strong pull either way

The conclusion is derived directly from the computed values with an
`if`/`elif`/`else` check, rather than assumed in advance — it confirms
whether the pattern already suggested by the histogram and box plot
(fare's long tail toward expensive 1st-class fares) holds up
numerically, and states the actual ordering as evidence.

*(Actual skew conclusion to be filled in from run output.)*

## Bivariate Analysis — Survival Rates and Correlation

Looks at relationships *between* variables (rather than one column
alone, as in the univariate section above): how survival rate varies
across groups, and which numeric features move together most strongly.

### Cells 20–22 — Survival rate by group (boolean masking)
Computes survival rate — the fraction of passengers who survived —
broken down three ways, using direct boolean masking (`df[condition]`)
rather than `.groupby()`, to demonstrate boolean indexing explicitly:
- **Cell 20 (by `sex`):** male vs. female survival rate
- **Cell 21 (by `pclass`):** 1st / 2nd / 3rd class survival rate
- **Cell 22 (by `sex` AND `pclass` together):** all six combinations
  (e.g. female+1st-class, male+3rd-class), using `&` to combine both
  conditions in a single mask

**Why `.mean()` on `survived` gives the rate directly:** since
`survived` is already `0`/`1`, averaging it over any filtered subset is
mathematically identical to (count of survivors) / (total in group) —
no separate counting step needed.

**Why each condition needs parentheses when combined with `&`:** pandas
evaluates `&` with higher precedence than `==`, so
`df["sex"] == "female" & df["pclass"] == 1` would be parsed incorrectly
without wrapping each comparison in its own parentheses first.

*(Actual survival rates to be filled in from run output.)*

### Cell 23 — Correlation matrix (6 specified columns)
Builds a correlation matrix using exactly `survived`, `pclass`, `age`,
`sibsp`, `parch`, `fare`.

**Why `adult_male` and `alone` are excluded:** both are derived flags,
not independently measured data — `adult_male` is fully computable from
`sex` + `age` (and was already dropped earlier in Cell 10), and `alone`
is fully computable from whether `sibsp` and `parch` are both zero.
Including a column that's just a re-expression of other columns already
in the matrix would inflate apparent correlations without adding any
real information.

**Why the 6 columns are explicitly selected (`df[corr_columns]`) rather
than running `.corr()` on the whole DataFrame:** `.corr()` silently
drops non-numeric columns on its own, but `alone` (boolean) would still
be numeric-compatible and could sneak into the matrix if not excluded
explicitly. Selecting exactly the required 6 columns first guarantees
nothing unwanted leaks in, regardless of dtype.

### Cell 24 — Heatmap of the correlation matrix
Renders the 6×6 matrix with `sns.heatmap`, using `cmap="coolwarm"` and
`center=0` so positive and negative correlations are visually
distinguishable by color (red vs. blue), with `annot=True` printing the
exact coefficient inside each cell for precise reading alongside the
color.

### Cell 25 — Two strongest correlations (by absolute value)
Finds the two off-diagonal pairs with the largest absolute correlation
coefficient — treating a strong negative correlation as equally
significant as a strong positive one, since both represent a real,
strong relationship between variables.

**Why absolute value is used for ranking, not raw value:** a
correlation of `-0.85` reflects just as strong a relationship as `+0.85`
— only the direction differs. Ranking by raw value would incorrectly
treat strong negative relationships as "weaker" than weak positive
ones.

**Why self-correlations and duplicate pairs are filtered out:**
`corr_matrix.unstack()` flattens the full grid, which includes each
variable's correlation with itself (always exactly `1.0`, meaningless
for this ranking) and lists every pair twice (e.g. both
`(pclass, fare)` and `(fare, pclass)`, identical values). Both are
filtered out so the "top 2" reflects two genuinely different
relationships, not an artifact of the matrix's symmetry.

*(Actual top 2 pairs, values, and written interpretation to be filled
in from run output.)*

## Multivariate Data Story — Who Was More Likely to Survive, and Why

Four charts that together build one coherent argument: **survival was
driven by a combination of sex, class/wealth, age, and family
circumstances — not any single factor alone.**

### Cell 26 — Chart 1: Bar chart — survival rate by class and sex
Grouped bar chart showing survival rate for each `pclass` × `sex`
combination.
**Interpretation:** *(to be filled in from actual bar heights)* This
chart is the foundation of the story: it shows survival rate splitting
sharply along both class and sex lines at once, not just one or the
other. If female passengers survive at a much higher rate than male
passengers within every class, and 1st class survives more than 3rd
within both sexes, it establishes that these two factors compound
rather than substitute for each other.

### Cell 27 — Chart 2: Box plot — age distribution, survived vs. did not
Compares the spread of `age` between passengers who survived and those
who didn't.
**Interpretation:** *(to be filled in from actual plot)* This adds age
as a second axis to the story. If the "survived" box sits slightly
lower (younger median) than the "did not survive" box, it suggests
children and younger passengers had somewhat better odds — consistent
with a "women and children first" boarding priority — though the
effect is likely smaller than the class/sex split in Chart 1.

### Cell 28 — Chart 3: Scatter plot — age vs. fare, colored by survival
Plots every passenger as a point (age on x-axis, fare on y-axis),
colored by whether they survived.
**Interpretation:** *(to be filled in from actual scatter pattern)*
This ties wealth (fare, a proxy for class) and age together in one
view. If survivors (one color) cluster more toward the higher-fare
region of the plot regardless of age, it reinforces that fare/class was
a stronger survival driver than age alone — visually connecting Charts
1 and 2 into a single picture.

### Cell 29 — Chart 4: Heatmap — survival rate by class and family size
A derived `family_size` column (`sibsp + parch + 1`) is created for
this chart specifically, then pivoted against `pclass` to show survival
rate for every class × family-size combination as a heatmap.
**Why `family_size` instead of `sibsp`/`parch` separately:** the two
raw counts (siblings/spouses, parents/children) are less meaningful
individually than the total number of family members traveling
together, which is what actually affects whether someone had help
boarding a lifeboat or got separated in the chaos.
**Interpretation:** *(to be filled in from actual heatmap pattern)*
This adds a final layer the first three charts don't capture: whether
traveling **alone** (family_size = 1) or in a **very large group**
hurt survival odds even within the same class, compared to a small
family (2–4 people) — testing whether class/sex/age are the whole
story, or whether family circumstance also mattered independently.

**Overall story:** Across all four charts, sex and class appear to be
the dominant, most consistent drivers of survival, with age and family
size acting as secondary, moderating factors that shift the odds
further within each class/sex group rather than overriding them.

*(Note: final interpretation paragraphs above should be revised to
state what the charts actually show, once run.)*

### `02_modeling.ipynb` — Part B: Modeling pipeline
*(to be added)*