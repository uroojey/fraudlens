# FraudLens — Project Structure

This matches the folder skeleton already created locally today, with additions for where future code/docs will live.

```
fraudlens/
├── data/
│   ├── Base.csv                     # Raw dataset (Day 2) — gitignored if large
│   └── cleaned_base.csv             # Cleaned/encoded dataset (Day 3)
│
├── notebooks/
│   ├── 01_data_exploration.ipynb    # Day 2 — first-pass EDA
│   ├── 02_data_cleaning.ipynb       # Day 3 — cleaning/encoding pipeline
│   └── 03_modeling.ipynb            # Days 4-5 — training, evaluation, model selection
│
├── models/
│   ├── fraud_model.pkl              # Day 5 — final trained classifier
│   ├── scaler.pkl                   # Day 5 — fitted StandardScaler
│   └── feature_columns.pkl          # Day 5 — expected column order/list
│
├── utils/
│   ├── preprocessing.py             # Day 6 — shared cleaning fn (notebook + app both import this)
│   └── explain.py                   # Day 7 — rule-based explanation helper
│
├── sample_data/
│   └── sample_transactions.csv      # Day 6 — small held-out sample for local testing/demoing
│
├── powerbi/
│   └── FraudLens_Report.pbix        # Days 8-9 — Power BI Desktop report file
│
├── screenshots/                     # Day 10 — final demo screenshots for README/LinkedIn
│
├── docs/                            # NEW today — houses all Day 2 design docs
│   ├── ARCHITECTURE.md
│   ├── SCHEMA.md
│   ├── API.md
│   ├── UI-WIREFRAMES.md
│   └── PROJECT-STRUCTURE.md (this file)
│
├── app.py                           # Day 6-7 — the Streamlit app entry point
├── requirements.txt                 # Day 8 — exact package versions for deployment
├── data_notes.md                    # Day 2-3 — dataset + cleaning decisions log
├── model_notes.md                   # Days 4-5 — model comparison + final choice log
├── PROJECT_LOG.md                   # NEW today — running daily log across the whole capstone
├── .gitignore                       # Already created (Python template)
└── README.md                        # Already created — expanded fully on Day 10
```

## Rationale for Key Decisions

**`docs/` folder (new today):** Keeps all planning/design documentation separate from working code and data, so the repo reads cleanly to anyone browsing it (recruiters included) — code and docs don't get mixed together in the root.

**`utils/` as shared logic:** `preprocessing.py` is imported by both `notebooks/03_modeling.ipynb` (during training) and `app.py` (during live prediction). This single-source-of-truth pattern directly prevents the #1 architectural risk flagged in both `ARCHITECTURE.md` and `SCHEMA.md` — training/serving mismatch.

**`models/` as three files together, not one:** the model, scaler, and feature list are versioned and saved as a set. If any one changes, all three should be re-saved together — this is called out explicitly in the Day 5-6 blueprint sections and in `SCHEMA.md`.

**No `backend/` or `api/` folder:** Consistent with today's tech stack decision — there is no separate backend server, so no folder is created to imply one exists.

**No `database/` or `migrations/` folder:** Consistent with the PRD's exclusion of persistent storage.

**`powerbi/` as its own top-level folder:** Keeps the Power BI artifact clearly separated from the Python side of the project, since it's built and maintained by a completely different tool (Power BI Desktop, not code).

**`PROJECT_LOG.md` (new today):** A running day-by-day log (separate from the detailed `dayN.md` LinkedIn/documentation files you already produce) — this one is purely internal, short-form, and answers "what happened each day and what changed" for quick reference across the whole 10-day arc.

## Where Future Code Will Live (quick reference for Days 3-10)

| Day | New files created |
|---|---|
| 2 | `data/Base.csv`, `notebooks/01_data_exploration.ipynb`, `data_notes.md` |
| 3 | `notebooks/02_data_cleaning.ipynb`, `data/cleaned_base.csv` |
| 4 | `notebooks/03_modeling.ipynb` (baseline model), `model_notes.md` |
| 5 | `notebooks/03_modeling.ipynb` (final model), `models/*.pkl` (all 3) |
| 6 | `app.py` (core), `utils/preprocessing.py`, `sample_data/sample_transactions.csv` |
| 7 | `app.py` (polish), `utils/explain.py` |
| 8 | `requirements.txt`, `powerbi/FraudLens_Report.pbix` (draft) |
| 9 | `powerbi/FraudLens_Report.pbix` (final) |
| 10 | `README.md` (final), `screenshots/*`, final `PROJECT_LOG.md` entry |
