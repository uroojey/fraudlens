# FraudLens — API Design

**Important scope note:** FraudLens has **no REST/HTTP backend** — this was confirmed in today's tech stack decision (Streamlit runs the model in-process; no separate server). So there are no traditional client-server "endpoints" in the conventional sense.

To still satisfy the PRD's need for defined, testable interfaces before implementation, this document specifies the **internal function-level contracts** that `app.py` relies on. These behave like an API in every practical sense (defined inputs, outputs, validation, and error cases) — they're just Python function calls instead of HTTP calls. This keeps Day 6 implementation unambiguous, which is the actual goal of this section.

If a future version adds a real API (see PRD Section 12, Future Scope), these same contracts would translate almost directly into REST endpoints — noted per function below.

---

## Function 1: `preprocess_transactions(df: pd.DataFrame) -> pd.DataFrame`

**Purpose:** Transform a raw uploaded CSV into the exact cleaned/encoded/scaled format the model expects. This is the single most important function in the app — it must exactly mirror the Day 3 training-time cleaning logic.

**Location:** `utils/preprocessing.py`

**Input:**
- `df`: raw Pandas DataFrame from the uploaded CSV, with the original (pre-encoding) column names

**Output:**
- Cleaned, encoded, scaled Pandas DataFrame, columns aligned to `feature_columns.pkl`

**Validation:**
- Confirms all required raw columns are present (compares against a known required-columns list)
- Confirms no unexpected data types (e.g., text in a numeric column) that would break scaling

**Error cases:**
| Case | Behavior |
|---|---|
| Missing required column(s) | Raise a caught exception with a friendly message: "Your file is missing column(s): X, Y — please check the expected format." |
| Empty file / zero rows | Friendly message: "The uploaded file has no data." |
| Non-CSV file uploaded | Streamlit's `file_uploader` type filter prevents this at the UI level (accept only `.csv`) |

**Future REST equivalent:** `POST /api/preprocess` — body: raw CSV; response: cleaned feature array or 400 error

---

## Function 2: `predict_fraud(features: pd.DataFrame, model, scaler) -> pd.DataFrame`

**Purpose:** Run the loaded model on preprocessed data and return predictions + probabilities.

**Location:** `app.py` (or a small `utils/predict.py` if it grows — decide during implementation, not today)

**Input:**
- `features`: output of `preprocess_transactions()`
- `model`: loaded `fraud_model.pkl` object
- `scaler`: loaded `scaler.pkl` object (applied inside this function if not already applied)

**Output:**
- Original dataframe plus two new columns: `fraud_prediction` (Fraud / Not Fraud) and `fraud_probability` (0–100%)

**Validation:**
- Confirms `features` column order matches what the model was trained on (via `feature_columns.pkl`)

**Error cases:**
| Case | Behavior |
|---|---|
| Column order/shape mismatch with trained model | Friendly message: "Something went wrong scoring this file — please contact the repo owner," logged internally for debugging |
| Model file missing/corrupted at startup | App shows a startup error banner instead of crashing silently |

**Future REST equivalent:** `POST /api/predict` — body: cleaned feature array; response: predictions + probabilities array or 500 error

---

## Function 3: `explain_flagged_transaction(row: pd.Series, feature_importances: dict) -> str`

**Purpose:** Produce a simple, plain-language reason for why a transaction was flagged, using the top 2-3 most important features present in that row.

**Location:** `utils/explain.py`

**Input:**
- `row`: a single transaction's data (post-prediction)
- `feature_importances`: precomputed dict of feature name → importance score (from the trained model, generated once in Day 5, saved alongside the model)

**Output:**
- A short string, e.g.: `"Flagged mainly due to unusually high transaction amount and new account age."`

**Validation:**
- Confirms `feature_importances` is non-empty
- Skips explanation generation entirely for non-flagged (predicted-clean) rows — this function is only called for the "Top Suspicious Transactions" view (per PRD FR-6)

**Error cases:**
| Case | Behavior |
|---|---|
| Row has no strong feature signal (all importances near zero) | Falls back to generic text: "Flagged by the model's overall risk score." |

**Future REST equivalent:** `GET /api/explain/{transaction_id}` — response: explanation string

---

## Function 4: `load_model_artifacts() -> tuple(model, scaler, feature_columns)`

**Purpose:** Load the three saved model files once at app startup (not on every prediction, for performance).

**Location:** `app.py` (top-level, using Streamlit's `@st.cache_resource` decorator so it only runs once per app instance)

**Input:** None (reads from fixed paths in `models/`)

**Output:** the three loaded objects

**Error cases:**
| Case | Behavior |
|---|---|
| Any of the 3 files missing | App shows a clear startup error: "Model files not found — this app cannot make predictions right now." rather than a raw Python traceback |

**Future REST equivalent:** N/A — this is a startup/initialization concern, not a per-request endpoint

---

## Summary Table — All Interfaces at a Glance

| Function | Purpose | Called When |
|---|---|---|
| `preprocess_transactions()` | Clean/encode/scale uploaded CSV | Every file upload |
| `predict_fraud()` | Run model, get predictions | Immediately after preprocessing |
| `explain_flagged_transaction()` | Plain-language reason for a flag | For each row shown in "Top Suspicious Transactions" |
| `load_model_artifacts()` | Load model/scaler/columns from disk | Once, at app startup |

No authentication is applied to any of these — consistent with the PRD's explicit exclusion of user accounts/auth for v1.0.
