"""
FraudLens — Streamlit App (Fraud Analyst View)
Upload a CSV of transactions, get fraud predictions with explanations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt

from utils.preprocessing import preprocess_transactions, PreprocessingError
from utils.explain import load_feature_importance, explain_transaction

# ---------- Page Config ----------
st.set_page_config(
    page_title="FraudLens — Fraud Detection",
    page_icon="🔍",
    layout="wide"
)

MODELS_DIR = "models"


# ---------- Load Model Artifacts (cached, runs once) ----------
@st.cache_resource
def load_model_artifacts():
    model_path = os.path.join(MODELS_DIR, "fraud_model.pkl")
    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    columns_path = os.path.join(MODELS_DIR, "feature_columns.pkl")
    importance_path = os.path.join(MODELS_DIR, "feature_importance.csv")

    missing = [p for p in [model_path, scaler_path, columns_path] if not os.path.exists(p)]
    if missing:
        return None, None, None, None, missing

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    feature_columns = joblib.load(columns_path)
    feature_importance = load_feature_importance(importance_path) if os.path.exists(importance_path) else None

    return model, scaler, feature_columns, feature_importance, []


model, scaler, feature_columns, feature_importance, missing_files = load_model_artifacts()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ℹ️ About FraudLens")
    st.markdown(
        "Trained on the **Bank Account Fraud Dataset** "
        "(NeurIPS 2022, feedzai) — 'Base' variant."
    )
    st.markdown("Upload a CSV of transactions to screen for fraud.")
    st.markdown("---")
    st.markdown("🔗 [GitHub](https://github.com/uroojey/fraudlens)")
    st.markdown("🔗 [LinkedIn](https://linkedin.com/in/uroojey)")

# ---------- Header ----------
st.title("🔍 FraudLens")
st.markdown("Upload a CSV of transactions to screen for fraud.")

if missing_files:
    st.error(
        "Model files not found — this app cannot make predictions right now. "
        f"Missing: {', '.join(missing_files)}"
    )
    st.stop()

# ---------- File Upload ----------
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Couldn't read this file — please make sure it's a valid CSV.")
        st.stop()

    try:
        with st.spinner("Processing transactions..."):
            df_processed = preprocess_transactions(df_raw, feature_columns)
            X_scaled = scaler.transform(df_processed)
            predictions = model.predict(X_scaled)
            probabilities = model.predict_proba(X_scaled)[:, 1]
    except PreprocessingError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error("Something went wrong scoring this file — please check the file format and try again.")
        st.stop()

    # Build results dataframe (original columns + predictions)
    results = df_raw.copy()
    results['fraud_prediction'] = np.where(predictions == 1, 'Fraud', 'Not Fraud')
    results['fraud_probability'] = (probabilities * 100).round(2)

    n_flagged = int((predictions == 1).sum())
    n_total = len(results)

    # ---------- Summary Metric ----------
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", f"{n_total:,}")
    col2.metric("Flagged as Fraud", f"{n_flagged:,}")
    col3.metric("Flag Rate", f"{(n_flagged / n_total * 100) if n_total else 0:.2f}%")

    # ---------- Distribution Chart ----------
    st.subheader("📊 Distribution: Normal vs. Fraud")
    fig, ax = plt.subplots(figsize=(6, 3))
    counts = [n_total - n_flagged, n_flagged]
    labels = ['Not Fraud', 'Fraud']
    colors = ['#02C39A', '#F96167']
    ax.barh(labels, counts, color=colors)
    ax.set_xlabel('Number of Transactions')
    for i, v in enumerate(counts):
        ax.text(v, i, f' {v:,}', va='center')
    st.pyplot(fig)

    # ---------- Top Suspicious Transactions ----------
    st.subheader("🔺 Top Suspicious Transactions")
    top_suspicious = results[results['fraud_prediction'] == 'Fraud'].sort_values(
        'fraud_probability', ascending=False
    ).head(20).copy()

    if len(top_suspicious) > 0:
        if feature_importance is not None:
            explanations = []
            for idx, row in top_suspicious.iterrows():
                explanations.append(explain_transaction(df_processed.loc[idx], feature_importance))
            top_suspicious['why_flagged'] = explanations
        else:
            top_suspicious['why_flagged'] = "Flagged by the model's overall risk score."

        display_cols = ['fraud_probability', 'why_flagged'] + [
            c for c in df_raw.columns if c in ['income', 'customer_age', 'payment_type', 'employment_status']
        ]
        st.dataframe(top_suspicious[display_cols], use_container_width=True)
    else:
        st.info("No transactions were flagged as fraud in this batch.")

    # ---------- Full Results Table ----------
    st.subheader("📋 Full Results")
    st.dataframe(results, use_container_width=True)

else:
    st.info("👆 Upload a CSV file to get started. Need a sample? Check the `sample_data/` folder in the repo.")

# ---------- Footer ----------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
    "Built with Claude as part of the AB Talks 60-Day Claude AI Challenge."
    "</div>",
    unsafe_allow_html=True
)
