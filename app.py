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
    page_title="FraudLens [Fraud Detection]",
    layout="wide"
)

MODELS_DIR = "models"
MAX_DISPLAY_ROWS = 5000

# ---------- Theme Definitions ----------
THEMES = {
    "Dark": {
        "bg": "#0B1C2C",
        "card_bg": "#1C3B4A",
        "border": "#02C39A",
        "text": "#FFFFFF",
        "muted": "#8FA8B2",
        "accent": "#02C39A",
        "accent2": "#F96167",
        "chart_face": "#1C3B4A",
        "chart_text": "#E8F0F2",
    },
    "Light": {
        "bg": "#F7FAFA",
        "card_bg": "#FFFFFF",
        "border": "#02A88A",
        "text": "#0B1C2C",
        "muted": "#5A6E76",
        "accent": "#02A88A",
        "accent2": "#E85A5F",
        "chart_face": "#FFFFFF",
        "chart_text": "#0B1C2C",
    },
}

if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = "Dark"

T = THEMES[st.session_state.theme_choice]

# ---------- Global Styling ----------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

    /* Base font for real text content only — icon glyphs are explicitly excluded below */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label,
    .stMarkdown, .stCaption, .stButton button, .stDownloadButton button {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
    }}

    /* Restore Streamlit's icon font for actual icon glyphs — must come after the
       broad rule above so it wins on source order for these specific elements. */
    [data-testid="stIconMaterial"],
    [data-testid*="Icon"],
    span[class*="material-icons"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="baseButton-header"] span {{
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }}

    .stApp {{
        background-color: {T['bg']};
    }}
    [data-testid="stHeader"] {{
        background-color: {T['bg']} !important;
        border-bottom: 1px solid {T['border']}22;
    }}
    [data-testid="stToolbar"] {{
        background-color: {T['bg']} !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {T['card_bg']};
    }}
    section[data-testid="stSidebar"] * {{
        color: {T['text']} !important;
    }}
    section[data-testid="stSidebar"] a {{
        color: {T['accent']} !important;
    }}

    .stButton button, .stDownloadButton button {{
        background-color: {T['accent']} !important;
        color: {T['bg'] if st.session_state.theme_choice == 'Light' else '#0B1C2C'} !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    .stButton button *, .stDownloadButton button * {{
        color: inherit !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        background-color: {T['card_bg']} !important;
        border: 1px dashed {T['border']}77 !important;
    }}
    [data-testid="stFileUploaderDropzone"] * {{
        color: {T['text']} !important;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
        background-color: {T['bg']} !important;
        color: {T['text']} !important;
    }}

    .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}

    div[data-testid="stMetric"] {{
        background-color: {T['card_bg']};
        border: 1px solid {T['border']}44;
        padding: 1rem 1rem 0.5rem 1rem;
        border-radius: 0.6rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(2,195,154,0.15);
    }}

    .fl-stat-card {{
        text-align:center;
        padding: 1.2rem 0.5rem;
        border-radius: 0.6rem;
        background-color: {T['card_bg']};
        border: 1px solid {T['border']}55;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .fl-stat-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(2,195,154,0.18);
    }}
    .fl-stat-number {{ font-family:'Space Grotesk', sans-serif; font-size:2rem; font-weight:700; color:{T['text']}; }}
    .fl-stat-label {{ color:{T['muted']}; font-size:0.85rem; margin-top:0.2rem; }}

    .fraudlens-empty-state {{
        text-align: center;
        padding: 3rem 1rem;
        color: {T['muted']};
    }}
    .fraudlens-empty-state h3 {{ color: {T['text']}; }}

    .stButton button, .stDownloadButton button {{
        transition: transform 0.12s ease, box-shadow 0.12s ease;
        border-radius: 0.5rem !important;
    }}
    .stButton button:hover, .stDownloadButton button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(2,195,154,0.25);
    }}

    .stDataFrame {{ border-radius: 0.5rem; overflow: hidden; }}
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
    st.markdown("### About FraudLens")
    st.markdown(
        "Trained on the **Bank Account Fraud Dataset** "
        "(NeurIPS 2022, feedzai) — 'Base' variant."
    )
    st.markdown("Upload a CSV of transactions to screen for fraud.")
    st.markdown("---")
    st.markdown("**Appearance**")
    st.radio(
        "Theme", options=["Dark", "Light"], key="theme_choice",
        horizontal=True, label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown(
        "1. Upload a CSV\n"
        "2. Transactions are cleaned and scored\n"
        "3. Review flagged transactions and why they were flagged"
    )
    st.markdown("---")
    st.markdown("[GitHub](https://github.com/uroojey/fraudlens)")
    st.markdown("[LinkedIn](https://linkedin.com/in/uroojey)")

# ---------- Header ----------
st.markdown(
    f"""
    <div style='padding: 1rem 0 0.5rem 0;'>
        <h1 style='font-size: 2.4rem; font-weight: 700; margin-bottom: 0.2rem; color:{T['text']};'>FraudLens</h1>
        <p style='font-size: 1.05rem; color: {T['muted']}; max-width: 640px;'>
        Real-time transaction screening for fraud analysts, powered by a machine
        learning model trained on real-world banking application data.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if missing_files:
    st.error(
        "Model files not found — this app cannot make predictions right now. "
        f"Missing: {', '.join(missing_files)}. Please contact the repo owner."
    )
    st.stop()

# ---------- Stat Callout Strip ----------
stat_col1, stat_col2, stat_col3 = st.columns(3)
stats = [("82%", "Fraud Recall"), ("1M+", "Transactions in Training Data"),
         ("&lt;5s", "Typical Screening Time")]
for col, (number, label) in zip([stat_col1, stat_col2, stat_col3], stats):
    with col:
        st.markdown(
            f"<div class='fl-stat-card'><div class='fl-stat-number'>{number}</div>"
            f"<div class='fl-stat-label'>{label}</div></div>",
            unsafe_allow_html=True
        )

st.markdown("<div style='padding-top:1.5rem;'></div>", unsafe_allow_html=True)

# ---------- File Upload ----------
sample_col1, sample_col2 = st.columns([3, 1])
with sample_col1:
    st.caption(
        "Don't have transaction data handy? Download a sample file to try the app.")
with sample_col2:
    sample_path = os.path.join("sample_data", "sample_transactions.csv")
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            st.download_button(
                "Download Sample CSV",
                data=f,
                file_name="sample_transactions.csv",
                mime="text/csv",
                use_container_width=True
            )

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
    help="File must include the standard transaction columns. Use the sample file above if you're not sure of the format."
)

if uploaded_file is not None:
    try:
        df_raw = read_uploaded_csv(uploaded_file)
    except PreprocessingError as e:
        st.error(str(e))
        st.stop()
    except Exception:
        st.error("Couldn't read this file — please make sure it's a valid CSV.")
        st.stop()

    if df_raw.empty:
        st.warning(
            "This file appears to be empty. Please upload a CSV with transaction rows.")
        st.stop()

    if len(df_raw) > 100_000:
        st.warning(
            f"This file has {len(df_raw):,} rows — very large files may take a while to process. "
            "Consider uploading a smaller batch for faster results."
        )

    try:
        with st.spinner("Screening transactions for fraud patterns..."):
            df_processed = preprocess_transactions(df_raw, feature_columns)
            X_scaled = scaler.transform(df_processed)
            predictions = model.predict(X_scaled)
            probabilities = model.predict_proba(X_scaled)[:, 1]
            X_scaled_df = pd.DataFrame(
                X_scaled, columns=feature_columns, index=df_processed.index)
    except PreprocessingError as e:
        st.error(str(e))
        st.stop()
    except Exception:
        st.error(
            "Something went wrong scoring this file. Please double-check the file format "
            "matches the expected columns, then try again."
        )
        st.stop()

    results = df_raw.copy()
    results['fraud_prediction'] = np.where(
        predictions == 1, 'Fraud', 'Not Fraud')
    results['fraud_probability'] = (probabilities * 100).round(2)

    n_flagged = int((predictions == 1).sum())
    n_total = len(results)
    flag_rate = (n_flagged / n_total * 100) if n_total else 0

    st.success(f"Screened {n_total:,} transactions successfully.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", f"{n_total:,}")
    col2.metric("Flagged as Fraud", f"{n_flagged:,}")
    col3.metric("Flag Rate", f"{flag_rate:.2f}%")

    st.markdown("")

    # ---------- Distribution Chart ----------
    st.subheader("Distribution: Normal vs. Fraud")
    fig, ax = plt.subplots(figsize=(7, 2.8))
    fig.patch.set_facecolor(T['chart_face'])
    ax.set_facecolor(T['chart_face'])
    counts = [n_total - n_flagged, n_flagged]
    labels = ['Not Fraud', 'Fraud']
    colors = [T['accent'], T['accent2']]
    ax.barh(labels, counts, color=colors, height=0.55)
    ax.set_xlabel('Number of Transactions', color=T['chart_text'])
    ax.tick_params(colors=T['chart_text'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(T['chart_text'])
    ax.spines['bottom'].set_color(T['chart_text'])
    for i, v in enumerate(counts):
        ax.text(v + max(counts) * 0.01, i,
                f'{v:,}', va='center', fontsize=10, color=T['chart_text'])
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")

    # ---------- Top Suspicious Transactions ----------
    st.subheader("Top Suspicious Transactions")
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
            "<div class='fraudlens-empty-state'>No transactions were flagged as fraud in this batch.</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ---------- Full Results Table ----------
    st.subheader("Full Results")
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
        <h3>Ready to screen your transactions</h3>
        <p>Upload a CSV file above to get started, or download the sample file if you don't have your own.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- Power BI Dashboard Preview ----------
st.markdown("---")
st.subheader("Business View: Power BI Report")
st.caption(
    "This is a snapshot of the companion Power BI report (Risk Manager view). "
    "It's a downloadable file rather than a live embed — open it in Power BI Desktop (free) to explore it interactively."
)
powerbi_screenshot = os.path.join("screenshots", "powerbi_dashboard.png")
if os.path.exists(powerbi_screenshot):
    st.image(powerbi_screenshot, use_container_width=True)
else:
    st.info("Power BI dashboard preview image not found.")

powerbi_file = os.path.join("powerbi", "FraudLens_Report.pbix")
if os.path.exists(powerbi_file):
    with open(powerbi_file, "rb") as f:
        st.download_button(
            "Download Power BI Report (.pbix)",
            data=f,
            file_name="FraudLens_Report.pbix",
            mime="application/octet-stream"
        )

# ---------- End of App ----------
