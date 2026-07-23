# FraudLens — Data Schema

**Note on scope:** Per the PRD (no auth, no persistence, no user accounts), FraudLens has **no traditional database**. All "storage" is flat files: the dataset CSV, the cleaned CSV, and serialized model artifacts. This document treats those flat files as the schema, since that's the actual persistent data shape in this project.

---

## 1. Raw Dataset — `data/Base.csv`

Source: Bank Account Fraud Dataset (NeurIPS 2022, feedzai), "Base" variant.

| Field (representative subset*) | Type | Description | Constraints |
|---|---|---|---|
| `fraud_bool` | int (0/1) | Target label — 1 if fraudulent | Required. This is the prediction target. |
| `income` | float | Applicant's income bracket (normalized) | May contain `-1` as "missing" placeholder |
| `name_email_similarity` | float | Similarity score between name and email | 0.0–1.0 |
| `customer_age` | int | Applicant age bucket | — |
| `employment_status` | categorical | Employment status code | One-hot encoded in cleaning step |
| `housing_status` | categorical | Housing status code | One-hot encoded in cleaning step |
| `payment_type` | categorical | Payment method used | One-hot encoded in cleaning step |
| `device_os` | categorical | Device operating system | One-hot encoded in cleaning step |
| `month` | int | Simulated month of application | **Flagged in Day 3 blueprint as a potential leakage column — verify before using as a feature** |
| ...remaining columns | numeric/categorical | Per Kaggle data dictionary | Documented per-column in `data_notes.md` during Day 2 |

*Full column list (~30 columns) is documented in `data_notes.md` once the dataset is downloaded in today's remaining Day 2 work — this table will be completed then, not invented today, since the PRD requires validating actual data, not assumed structure.

**Validation rule:** every column used as a model feature must be confirmed as "known at prediction time" — i.e., not derived from information only available after a fraud determination is made. This is checked during Day 3 cleaning.

---

## 2. Cleaned Dataset — `data/cleaned_base.csv`

Same row structure as `Base.csv`, transformed as follows:

| Transformation | Applied To | Rule |
|---|---|---|
| Missing value handling | Columns using `-1` as missing placeholder | Impute or flag-as-category per column (decided in Day 3, documented in `data_notes.md`) |
| One-hot encoding | All categorical columns (`payment_type`, `employment_status`, `housing_status`, `device_os`, etc.) | Expands each category into binary columns |
| Leakage column removal | `month` (if confirmed as leakage) | Dropped entirely if not safe to use |
| Target isolation | `fraud_bool` | Kept separate as `y`; not scaled |

**Constraint:** `cleaned_base.csv` must have zero null values and be 100% numeric (verified in Day 3 testing tasks) — this is what makes it "model-ready."

---

## 3. Model Artifacts — `models/`

These three files together form the "schema" the Streamlit app depends on. All three must be saved together and stay in sync — this is the #1 architectural risk flagged in the blueprint (Day 6 debugging notes).

| File | Contents | Produced By | Consumed By |
|---|---|---|---|
| `fraud_model.pkl` | Trained classifier object (Logistic Regression or Random Forest, whichever wins evaluation) | Day 5 notebook | `app.py` |
| `scaler.pkl` | Fitted `StandardScaler` object (fit only on training data) | Day 4-5 notebook | `app.py` (applied to new uploads before prediction) |
| `feature_columns.pkl` | Ordered list of column names the model expects, post-encoding | Day 5 notebook | `app.py` (used to validate/align uploaded CSV columns) |

**Constraint validated in Day 6 testing:** reloading these three files in a fresh session and predicting on a held-out sample must produce identical results to the original notebook evaluation. If not, the artifacts are out of sync and must be re-saved together.

---

## 4. Runtime Input — User-Uploaded CSV (Streamlit)

This is not stored anywhere — it exists only in memory during a single browser session.

| Requirement | Rule |
|---|---|
| Required columns | Must match `feature_columns.pkl` (pre-encoding raw columns) |
| Row limit | No hard limit for v1.0, but very large files may be slow — acceptable per PRD (no real-time/streaming requirement) |
| Validation | If required columns are missing, app shows a friendly error rather than crashing (Day 6 requirement) |
| Persistence | None — data is discarded when the browser tab closes or a new file is uploaded |

---

## 5. Power BI Data Source

The `.pbix` file (built in Power BI Desktop, Day 8-9) imports `cleaned_base.csv` directly as a static import (not a live/scheduled refresh connection), since there's no hosted database to connect to. This is consistent with the "Desktop artifact, not live service" decision made today.

---

## 6. Schema Validation Against PRD User Stories

| PRD Requirement | Schema Support |
|---|---|
| FR-1: Upload CSV of transactions | Runtime input schema (Section 4) supports this |
| FR-2: Fraud prediction + probability per transaction | Model artifacts (Section 3) directly enable this |
| FR-6: Plain-language explanation using feature importance | Requires `fraud_model.pkl` to expose `.feature_importances_` (Random Forest) or `.coef_` (Logistic Regression) — both supported by the chosen algorithms |
| FR-7/FR-8: Power BI trend/category visuals + DAX measure | `cleaned_base.csv` (Section 2) has the categorical + target columns needed |

No PRD requirement needs data storage beyond what's listed above — confirms no database is needed for v1.0.
