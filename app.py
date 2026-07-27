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
MAX_DISPLAY_ROWS = 5000  # guard against extremely large files slowing down the browser

# ---------- Light Custom Styling ----------
st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background-color: rgba(2, 195, 154, 0.08);
        border: 1px solid rgba(2, 195, 154, 0.25);
        padding: 1rem 1rem 0.5rem 1rem;
        border-radius: 0.6rem;
    }
    .fraudlens-empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #8FA8B2;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------- Load Model Artifacts (cached, runs once) ----------
@st.cache_resource
def load_model_artifacts():
    model_path = os.path.join(MODELS_DIR, "fraud_model.pkl")
    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    columns_path = os.path.join(MODELS_DIR, "feature_columns.pkl")
    importance_path = os.path.join(MODELS_DIR, "feature_importance.csv")

    missing = [p for p in [model_path, scaler_path,
                           columns_path] if not os.path.exists(p)]
    if missing:
        return None, None, None, None, missing

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    feature_columns = joblib.load(columns_path)
    feature_importance = load_feature_importance(
        importance_path) if os.path.exists(importance_path) else None

    return model, scaler, feature_columns, feature_importance, []


def read_uploaded_csv(uploaded_file):
    """Read an uploaded CSV with a fallback encoding chain, raising a friendly error on failure."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            raise PreprocessingError("The uploaded file has no data.")
        except pd.errors.ParserError:
            raise PreprocessingError(
                "This file couldn't be parsed as a CSV — please check it's correctly formatted "
                "(comma-separated, no corrupted rows)."
            )
    raise PreprocessingError(
        "Couldn't read this file's text encoding. Please save it as UTF-8 CSV and try again."
    )


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
    st.markdown("**How it works:**")
    st.markdown(
        "1. Upload a CSV\n"
        "2. Transactions are cleaned and scored\n"
        "3. Review flagged transactions and why they were flagged"
    )
    st.markdown("---")
    st.markdown("🔗 [GitHub](https://github.com/uroojey/fraudlens)")
    st.markdown("🔗 [LinkedIn](https://linkedin.com/in/uroojey)")

# ---------- Header ----------
st.title("🔍 FraudLens")
st.caption("Upload a CSV of transactions to screen for fraud in seconds.")

if missing_files:
    st.error(
        "⚠️ Model files not found — this app cannot make predictions right now. "
        f"Missing: {', '.join(missing_files)}. Please contact the repo owner."
    )
    st.stop()

# ---------- File Upload ----------
uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
    help="File must include the standard transaction columns. See sample_data/ in the repo for an example."
)

if uploaded_file is not None:
    try:
        df_raw = read_uploaded_csv(uploaded_file)
    except PreprocessingError as e:
        st.error(f"⚠️ {str(e)}")
        st.stop()
    except Exception:
        st.error("⚠️ Couldn't read this file — please make sure it's a valid CSV.")
        st.stop()

    if df_raw.empty:
        st.warning(
            "This file appears to be empty. Please upload a CSV with transaction rows.")
        st.stop()

    if len(df_raw) > 100_000:
        st.warning(
            f"⚠️ This file has {len(df_raw):,} rows — very large files may take a while to process. "
            "Consider uploading a smaller batch for faster results."
        )

    try:
        with st.spinner("🔎 Screening transactions for fraud patterns..."):
            df_processed = preprocess_transactions(df_raw, feature_columns)
            X_scaled = scaler.transform(df_processed)
            predictions = model.predict(X_scaled)
            probabilities = model.predict_proba(X_scaled)[:, 1]
            # Keep a scaled-value dataframe (same index/columns as df_processed)
            # for use in explanations — using scaled values here matches the
            # units the model's coefficients were actually trained on, giving
            # more accurate "why flagged" reasoning than using raw values would.
            X_scaled_df = pd.DataFrame(
                X_scaled, columns=feature_columns, index=df_processed.index)
    except PreprocessingError as e:
        st.error(f"⚠️ {str(e)}")
        st.stop()
    except Exception:
        st.error(
            "⚠️ Something went wrong scoring this file. Please double-check the file format "
            "matches the expected columns, then try again."
        )
        st.stop()

    # Build results dataframe (original columns + predictions)
    results = df_raw.copy()
    results['fraud_prediction'] = np.where(
        predictions == 1, 'Fraud', 'Not Fraud')
    results['fraud_probability'] = (probabilities * 100).round(2)

    n_flagged = int((predictions == 1).sum())
    n_total = len(results)
    flag_rate = (n_flagged / n_total * 100) if n_total else 0

    st.success(f"✅ Screened {n_total:,} transactions successfully.")

    # ---------- Summary Metrics ----------
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", f"{n_total:,}")
    col2.metric("Flagged as Fraud", f"{n_flagged:,}")
    col3.metric("Flag Rate", f"{flag_rate:.2f}%")

    st.markdown("")  # small spacer

    # ---------- Distribution Chart ----------
    st.subheader("📊 Distribution: Normal vs. Fraud")
    fig, ax = plt.subplots(figsize=(7, 2.8))
    counts = [n_total - n_flagged, n_flagged]
    labels = ['Not Fraud', 'Fraud']
    colors = ['#02C39A', '#F96167']
    ax.barh(labels, counts, color=colors, height=0.55)
    ax.set_xlabel('Number of Transactions')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for i, v in enumerate(counts):
        ax.text(v + max(counts) * 0.01, i, f'{v:,}', va='center', fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)
    # prevents figure accumulation across repeated uploads in one session
    plt.close(fig)

    st.markdown("---")

    # ---------- Top Suspicious Transactions ----------
    st.subheader("🔺 Top Suspicious Transactions")
    top_suspicious = results[results['fraud_prediction'] == 'Fraud'].sort_values(
        'fraud_probability', ascending=False
    ).head(20).copy()

    if len(top_suspicious) > 0:
        if feature_importance is not None:
            explanations = []
            for idx in top_suspicious.index:
                explanations.append(explain_transaction(
                    X_scaled_df.loc[idx], feature_importance))
            top_suspicious['why_flagged'] = explanations
        else:
            top_suspicious['why_flagged'] = "Flagged by the model's overall risk score."

        display_cols = ['fraud_probability', 'why_flagged'] + [
            c for c in df_raw.columns if c in ['income', 'customer_age', 'payment_type', 'employment_status']
        ]
        st.dataframe(
            top_suspicious[display_cols].rename(columns={
                'fraud_probability': 'Fraud Probability (%)',
                'why_flagged': 'Why Flagged',
                'income': 'Income',
                'customer_age': 'Age',
                'payment_type': 'Payment Type',
                'employment_status': 'Employment Status',
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.markdown(
            "<div class='fraudlens-empty-state'>✅ No transactions were flagged as fraud in this batch.</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ---------- Full Results Table ----------
    st.subheader("📋 Full Results")
    if n_total > MAX_DISPLAY_ROWS:
        st.caption(
            f"Showing the first {MAX_DISPLAY_ROWS:,} of {n_total:,} screened transactions "
            "(large result sets are truncated for display performance)."
        )
        st.dataframe(results.head(MAX_DISPLAY_ROWS),
                     use_container_width=True, hide_index=True)
    else:
        st.caption(
            f"All {n_total:,} screened transactions, sortable by any column.")
        st.dataframe(results, use_container_width=True, hide_index=True)

else:
    st.markdown(
        """
        <div class='fraudlens-empty-state'>
        <h3>👋 Ready to screen your transactions</h3>
        <p>Upload a CSV file above to get started.<br>
        Need a sample? Check the <code>sample_data/</code> folder in the repo.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- End of App ----------
