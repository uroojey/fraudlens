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
