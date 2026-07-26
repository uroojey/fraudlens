"""
One-time script: computes the median imputation values used during Day 3 cleaning,
using the RAW dataset (Base.csv), and saves them so the live app can apply the
exact same imputation to new uploaded transactions.

Run this once, from the project root, with your venv activated:
    python save_imputation_values.py
"""

import pandas as pd
import json

RAW_PATH = "data/Base.csv"
OUTPUT_PATH = "models/imputation_values.json"

df = pd.read_csv(RAW_PATH)

num_cols_median = ['current_address_months_count', 'bank_months_count', 'session_length_in_minutes']

imputation_values = {}
for col in num_cols_median:
    valid_median = df.loc[df[col] != -1, col].median()
    imputation_values[col] = float(valid_median)
    print(f"{col}: median = {valid_median}")

with open(OUTPUT_PATH, 'w') as f:
    json.dump(imputation_values, f, indent=2)

print(f"\nSaved imputation values to {OUTPUT_PATH}")
