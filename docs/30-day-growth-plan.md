# FraudLens — 30-Day Growth Plan
**From MVP to a significantly more complete product**

Each day builds on the previous one. Estimated 1-2 hours/day, matching your established pace.

## Week 1: Explainability & Model Rigor

- **Day 1:** Set up SHAP (`pip install shap`) in a new notebook; generate SHAP values for your existing Logistic Regression model on the test set.
- **Day 2:** Build a SHAP summary plot (global feature importance) and compare it against Day 5's coefficient-based ranking — do they agree?
- **Day 3:** Implement per-transaction SHAP explanations (force plot or waterfall) for the top 5 suspicious transactions from your sample data.
- **Day 4:** Replace `utils/explain.py`'s rule-based logic with SHAP-based explanations behind a feature flag (keep the old logic as fallback).
- **Day 5:** Update the Streamlit app to render SHAP explanations visually (bar chart per transaction) instead of just text.
- **Day 6:** Write up a comparison doc: rule-based vs. SHAP explanations — which is more trustworthy, which is faster, trade-offs.
- **Day 7:** Retrain on the full 1,000,000-row dataset (not the 200K sample) and re-run Day 5's model comparison at full scale — does Logistic Regression still win?

## Week 2: Real-Time Scoring API

- **Day 8:** Set up a minimal FastAPI project (`pip install fastapi uvicorn`) in a new `api/` folder.
- **Day 9:** Build a single `/predict` endpoint accepting one transaction's JSON, reusing `utils/preprocessing.py`.
- **Day 10:** Add request validation (Pydantic models) — reject malformed requests with clear error messages.
- **Day 11:** Test the API locally with sample requests (Postman or `curl`); write 5 test cases covering valid input, missing fields, and bad data types.
- **Day 12:** Deploy the API to Render's free tier (separate from your Streamlit app).
- **Day 13:** Add a "Single Transaction Check" tab to the Streamlit app that calls this new API instead of requiring a full CSV upload.
- **Day 14:** Write API documentation (a simple `API.md` update) with example requests/responses.

## Week 3: Threshold Control & Fairness Study

- **Day 15:** Add a Streamlit slider letting users adjust the fraud-flagging threshold live, recalculating predictions from stored probabilities (no retraining needed).
- **Day 16:** Show live precision/recall trade-off numbers next to the slider so users understand the effect of their choice.
- **Day 17:** Download the dataset's other 5 fairness variants from Kaggle (same source, different bias conditions).
- **Day 18:** Train your existing pipeline on one additional variant; compare fraud rates and model performance across protected groups.
- **Day 19:** Write a short fairness findings report — document any disparities found, honestly, without overclaiming conclusions.
- **Day 20:** Add a "Model Transparency" page to the Streamlit app summarizing these fairness findings for transparency with real users.
- **Day 21:** Review and refactor `utils/` folder — by now it's grown; clean up any duplicated logic between the SHAP work and original explain.py.

## Week 4: Case Management & Monitoring

- **Day 22:** Design a minimal database schema (SQLite, free, file-based — no new hosting needed) for storing review status per transaction: `reviewed`, `confirmed_fraud`, `false_positive`.
- **Day 23:** Add a lightweight local database connection to the Streamlit app; let users mark a transaction's review status.
- **Day 24:** Add a "Review Queue" view showing only unreviewed flagged transactions.
- **Day 25:** Build a simple model-monitoring script: compare current predictions' probability distribution against Day 5's original test set distribution, flag if drift looks significant.
- **Day 26:** Schedule this monitoring script to run weekly (using GitHub Actions free tier — a cron-style workflow file).
- **Day 27:** Add a "Model Health" section to the Power BI report showing this drift metric over time.
- **Day 28:** Write updated documentation: `MONITORING.md` explaining what's tracked and why.
- **Day 29:** Full regression test — walk through every feature (Streamlit, API, Power BI) end-to-end, confirm nothing from Weeks 1-3 broke anything else.
- **Day 30:** Write a "v2.0" retrospective, mirroring your Day 10 capstone retrospective — what changed, what you learned, what's next after 30 more days.