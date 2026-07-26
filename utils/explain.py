"""
FraudLens — Rule-Based Explanation Module

Produces a plain-language reason for why a transaction was flagged,
using the trained model's feature importances (Logistic Regression coefficients).
No SHAP/LIME — a simple, transparent rule-based approach, per project scope.
"""

import pandas as pd


def load_feature_importance(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def explain_transaction(row: pd.Series, feature_importance: pd.DataFrame, top_n: int = 3) -> str:
    """
    row: a single preprocessed transaction (post-encoding, matches feature_columns)
    feature_importance: dataframe with 'feature' and 'coefficient' columns
    """
    if feature_importance is None or feature_importance.empty:
        return "Flagged by the model's overall risk score."

    fi = feature_importance.set_index('feature')['coefficient']

    contributions = []
    for feat, coef in fi.items():
        if feat in row.index:
            value = row[feat]
            # For binary/dummy columns, only count contribution if the feature is "active" (1)
            # For continuous columns, use the coefficient sign/magnitude directly
            contribution = coef * value if value != 0 else 0
            if contribution != 0:
                contributions.append((feat, contribution))

    if not contributions:
        return "Flagged by the model's overall risk score."

    # Sort by how much each feature pushed toward "Fraud" (positive contribution)
    contributions.sort(key=lambda x: x[1], reverse=True)
    top_positive = [c for c in contributions[:top_n] if c[1] > 0]

    if not top_positive:
        return "Flagged by the model's overall risk score."

    readable_names = [f[0].replace('_', ' ') for f in top_positive]
    return "Flagged mainly due to: " + ", ".join(readable_names) + "."
