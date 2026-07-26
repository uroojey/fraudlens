# Data Notes — FraudLens

## Dataset Overview (Day 2)
- Source: Bank Account Fraud Dataset (NeurIPS 2022, feedzai), "Base" variant, via Kaggle
- Shape: 1,000,000 rows × 32 columns
- Target column: `fraud_bool`

## Class Balance
- Legitimate (0): 988,971 rows (98.90%)
- Fraudulent (1): 11,029 rows (1.10%)
- Highly imbalanced — will require `class_weight='balanced'` in Day 4 modeling, not naive accuracy as the evaluation metric

## Missing Value Pattern
- `-1` used as a missing-value placeholder in several columns (confirmed in `prev_address_months_count`)
- To be handled column-by-column in Day 3 cleaning

## Open Question for Day 3
- `days_since_request` shows some unusually large values alongside small ones — check distribution before deciding whether to cap/transform

# Data Cleaning Decisions & Rationale (Day 3)
## Cleaning Decisions Summary (copy into `data_notes.md`)

- Missing values (`-1` placeholders) handled per-column: median imputation for 3 columns, zero-imputation for 1, explicit 'MISSING' category for 1 — with `_is_missing` flag columns preserved for each.
- `month` column reviewed for leakage risk — see decision note in Step 2 output above.
- Categorical columns one-hot encoded with `drop_first=True`: `payment_type`, `employment_status`, `housing_status`.
- Dropped zero-variance column: `device_fraud_count`.
- Final dataset validated as zero-null, fully numeric, ready for Day 4 train/test split.
