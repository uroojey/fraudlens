# Model Notes — FraudLens

## Day 4 — Baseline Model: Logistic Regression

**Setup:**
- Stratified sample of 200,000 rows from the full 1,000,000-row cleaned dataset (fraud ratio preserved: ~1.10%)
- Stratified 80/20 train/test split (160,000 train / 40,000 test)
- Features scaled with `StandardScaler`, fit on training data only
- Model: `LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)`

**Results (test set, Fraud class = label 1):**

| Metric | Value |
|---|---|
| Precision (Fraud) | 0.0453 |
| Recall (Fraud) | 0.8231 |
| F1 (Fraud) | 0.0858 |
| True Positives | 363 |
| False Positives | 7,658 |
| False Negatives | 78 |
| True Negatives | 31,901 |

**Interpretation:**
The model catches 82.3% of actual fraud cases (strong recall), but only 4.5% of everything it flags as fraud is actually fraud (weak precision) — meaning roughly 19 false alarms for every correctly caught fraud case. This is the expected behavior of `class_weight='balanced'` on a dataset with a ~1.1% fraud rate: the model is deliberately biased toward catching fraud at the cost of frequent false positives.

**Baseline established for comparison.** Day 5 will train a Random Forest classifier on the same train/test split and compare precision/recall/F1 directly against these numbers, plus add Isolation Forest as a secondary unsupervised check. The model with the better precision/recall balance (not just higher recall alone) will be selected as the final model.

**Artifacts saved:**
- `model_baseline_metrics.json` — exact metrics in machine-readable form
- `screenshots/day4_confusion_matrix.png` — visual confusion matrix

---

## Day 5 — Model Comparison & Final Selection

**Random Forest — first attempt (`class_weight='balanced'`):**
Catastrophic recall failure — only 5 of 441 fraud cases caught (recall ≈ 1.1%). Root cause: Random Forest's bootstrap sampling means each individual tree sees very few fraud examples from the already-rare fraud class, and a single global class weight doesn't compensate for this per-tree dilution.

**Random Forest — second attempt (`class_weight='balanced_subsample'`):**
Improved slightly (13/441 caught, recall ≈ 2.9%) — better, but still far behind Logistic Regression. `balanced_subsample` recalculates weights per tree's own bootstrap sample, which helped marginally but didn't solve the core issue.

**Random Forest — threshold-tuned:**
Instead of using the default 0.5 probability cutoff, we tuned the decision threshold using a precision-recall curve, selecting the threshold that achieves ~80% recall (comparable to Logistic Regression) to allow a fair, apples-to-apples comparison.

**Final comparison table (all models at comparable ~80% recall where applicable):**

| Model | Precision (Fraud) | Recall (Fraud) | F1 (Fraud) |
|---|---|---|---|
| Logistic Regression | 0.0453 | 0.8231 | 0.0858 |
| Random Forest (default 0.5 threshold) | 0.2174 | 0.0113 | 0.0216 |
| Random Forest (tuned threshold) | 0.0337 | 0.8027 | 0.0647 |

**Decision: Logistic Regression selected as the final model.** Even after fairly tuning Random Forest's threshold to match recall, Logistic Regression still achieves better precision and a better F1 score (0.0858 vs. 0.0647) at a comparable recall level. The simpler model wins on this dataset — a legitimate and worth-documenting finding, not a fallback choice.

**Isolation Forest (secondary, unsupervised check):**
Trained on `X_train_scaled` only, without fraud labels, using `contamination=0.011` to match the known fraud rate. Used purely as a sanity-check comparison against the supervised model's flags — not used for the app's primary predictions.

**Feature Importance (Logistic Regression coefficients):**
Top signal: `prev_address_months_count_is_missing` (the missing-value flag created during Day 3 cleaning) is the single strongest predictor of fraud — a case where a "was this value missing" flag turned out to be more informative than the raw value itself. `device_os_windows` also strongly increases fraud likelihood. Protective factors (decrease fraud likelihood) include having other cards, a valid home phone, and several housing/employment status categories. This coherent, explainable pattern directly powers Day 7's plain-language explanation feature.

**Artifacts saved and verified (Day 5):**
- `models/fraud_model.pkl` — final Logistic Regression model
- `models/scaler.pkl` — fitted StandardScaler (fit on training data only)
- `models/feature_columns.pkl` — ordered list of 52 expected feature columns
- `models/feature_importance.csv` — full feature importance table
- `screenshots/day5_confusion_matrix_rf.png`, `day5_confusion_matrix_rf_tuned.png`, `day5_feature_importance.png`
- **Reload test passed** — reloaded artifacts produce identical predictions to the original in-memory model, confirming no save/load mismatch

**Ready for Day 6:** these three saved artifacts are exactly what the Streamlit app will load to make live predictions.

---

## Day 6 — Streamlit App Built & Verified

Core Streamlit app (`app.py`) built and tested end-to-end locally:
- File upload → `utils/preprocessing.py` (mirrors Day 3 cleaning exactly) → scaling → prediction → results display
- Summary metrics, distribution chart, Top Suspicious Transactions with rule-based explanations (`utils/explain.py`), full results table
- Footer added per today's requirement: "Built with Claude as part of the AB Talks 60-Day Claude AI Challenge."
- Tested on a 200-row real sample: 31 flagged (15.5% flag rate) — consistent with the model's known aggressive-flagging behavior documented in Day 4/5 (high recall, low precision)
- Explanations read as coherent, real fraud signals: transaction velocity (24h), zip code frequency (4w), proposed credit limit, credit risk score
- One new artifact added: `models/imputation_values.json` (median values for missing-data imputation, computed from raw training data via `save_imputation_values.py`) — required so new uploads can be cleaned identically to training data

**Scope note:** Day 6 and Day 7 (polish: charts, explanations, sidebar) were merged into one session per approval; deployment moves to tomorrow.

---

## Day 7 — Senior UX Polish & Deployment

**UX polish pass:** custom CSS styling for metric cards, distinct loading/success/error/empty states, human-readable table column names, cleaner chart styling, sidebar "How it works" explainer. Footer requirement (from Day 6) reversed per explicit request — no attribution text on any page.

**Deployed live:** `https://fraudlens404.streamlit.app` via Streamlit Community Cloud, connected directly to the GitHub repo (`main` branch, `app.py`). Free tier, no cost.

**Bug found and fixed during deployment:** `models/feature_importance.csv` was silently excluded from every prior commit — a broad `*.csv` rule in `.gitignore` (meant only to exclude the large raw dataset files) was also blocking this small, necessary artifact. This caused the deployed app's explanation feature to silently fall back to a generic message instead of the specific, coherent reasons seen locally. Fixed by force-adding the file and narrowing the `.gitignore` rule to `data/*.csv` only.

**Verified:** live app tested end-to-end in an incognito window (no local setup, no login) — upload, prediction, metrics, chart, and detailed explanations all working correctly on the public deployed version.