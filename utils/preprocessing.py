"""
FraudLens — Shared Preprocessing Module

This module replicates the exact cleaning/encoding logic used in
notebooks/02_data_cleaning.ipynb, so that new uploaded transactions
are transformed identically to how the training data was prepared.
"""

import pandas as pd
import numpy as np
import json
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMPUTATION_PATH = os.path.join(_CURRENT_DIR, '..', 'models', 'imputation_values.json')

NUM_COLS_MEDIAN = ['current_address_months_count', 'bank_months_count', 'session_length_in_minutes']
NUM_COLS_ZERO = ['prev_address_months_count']
CAT_COLS_FLAG = ['device_distinct_emails_8w']
CATEGORICAL_COLS = ['payment_type', 'employment_status', 'housing_status', 'source', 'device_os', 'device_distinct_emails_8w']
DROP_COLS = ['device_fraud_count']

REQUIRED_RAW_COLUMNS = list(set(
    NUM_COLS_MEDIAN + NUM_COLS_ZERO + CAT_COLS_FLAG + CATEGORICAL_COLS
))


class PreprocessingError(Exception):
    """Raised when an uploaded CSV can't be processed (missing columns, etc.)."""
    pass


def _load_imputation_values():
    if not os.path.exists(IMPUTATION_PATH):
        raise PreprocessingError(
            "Missing models/imputation_values.json. Run save_imputation_values.py first."
        )
    with open(IMPUTATION_PATH, 'r') as f:
        return json.load(f)


def validate_columns(df: pd.DataFrame):
    missing = [c for c in REQUIRED_RAW_COLUMNS if c not in df.columns]
    if missing:
        raise PreprocessingError(
            f"Your file is missing required column(s): {', '.join(missing)} — "
            f"please check the expected format."
        )


def preprocess_transactions(df_raw: pd.DataFrame, feature_columns: list) -> pd.DataFrame:
    """
    Transform a raw uploaded CSV into the exact cleaned/encoded format
    the model expects. Mirrors notebooks/02_data_cleaning.ipynb.
    """
    if df_raw.empty:
        raise PreprocessingError("The uploaded file has no data.")

    validate_columns(df_raw)

    df = df_raw.copy()
    imputation_values = _load_imputation_values()

    # Step 1: Handle missing values (-1 placeholders)
    for col in NUM_COLS_MEDIAN:
        df[f'{col}_is_missing'] = (df[col] == -1).astype(int)
        df[col] = df[col].replace(-1, imputation_values[col])

    for col in NUM_COLS_ZERO:
        df[f'{col}_is_missing'] = (df[col] == -1).astype(int)
        df[col] = df[col].replace(-1, 0)

    for col in CAT_COLS_FLAG:
        df[col] = df[col].astype(str).replace(['-1.0', '-1'], 'MISSING')

    # Step 2: One-hot encode categoricals
    df = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True, dtype=int)

    # Step 3: Drop redundant columns
    for col in DROP_COLS:
        if col in df.columns:
            df = df.drop(columns=[col])

    # Step 4: Align to the exact feature set the model was trained on.
    # Any dummy column not present in this batch (e.g., a category that
    # didn't appear in the uploaded file) is filled with 0.
    df = df.reindex(columns=feature_columns, fill_value=0)

    return df
