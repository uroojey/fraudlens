import os
import pandas as pd
import numpy as np

def generate_and_save_cleaned_base(file_path: str, output_path: str = "data/cleaned_base.csv"):
    df = pd.read_csv(file_path)
    print(f"Loaded raw dataset shape: {df.shape}")
    
    # 1. Handle Missing Values
    num_cols_median = ['current_address_months_count', 'bank_months_count', 'session_length_in_minutes']
    num_cols_zero = ['prev_address_months_count']
    cat_cols_flag = ['device_distinct_emails_8w']
    
    for col in num_cols_median:
        if (df[col] == -1).any():
            df[f'{col}_is_missing'] = (df[col] == -1).astype(int)
            valid_median = df.loc[df[col] != -1, col].median()
            df[col] = df[col].replace(-1, valid_median)
            
    for col in num_cols_zero:
        if (df[col] == -1).any():
            df[f'{col}_is_missing'] = (df[col] == -1).astype(int)
            df[col] = df[col].replace(-1, 0)

    for col in cat_cols_flag:
        if (df[col] == -1).any():
            df[col] = df[col].astype(str).replace(['-1.0', '-1'], 'MISSING')

    # 2. One-Hot Encode Categorical Columns
    categorical_cols = ['payment_type', 'employment_status', 'housing_status']
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True, dtype=int)
    
    # 3. Remove Redundant Columns
    if 'device_fraud_count' in df.columns:
        df = df.drop(columns=['device_fraud_count'])

    # 4. Save clean data
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned dataset successfully saved to: {output_path}")
    print(f"Final saved shape: {df.shape}")

if __name__ == "__main__":
    generate_and_save_cleaned_base("data/Base.csv")
