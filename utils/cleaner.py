from __future__ import annotations

import numpy as np
import pandas as pd


def basic_clean_data(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
    drop_empty_rows: bool = True,
    drop_empty_columns: bool = True,
    fill_numeric_missing: bool = False,
    fill_categorical_missing: bool = False,
) -> tuple[pd.DataFrame, dict]:
    cleaned_df = df.copy()

    summary = {
        "original_shape": df.shape,
        "duplicates_removed": 0,
        "empty_rows_removed": 0,
        "empty_columns_removed": [],
        "numeric_filled": {},
        "categorical_filled": {},
        "final_shape": None,
    }

    if remove_duplicates:
        before = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        summary["duplicates_removed"] = before - len(cleaned_df)

    if drop_empty_rows:
        before = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(axis=0, how="all")
        summary["empty_rows_removed"] = before - len(cleaned_df)

    if drop_empty_columns:
        empty_cols = cleaned_df.columns[cleaned_df.isna().all()].tolist()
        if empty_cols:
            cleaned_df = cleaned_df.drop(columns=empty_cols)
        summary["empty_columns_removed"] = empty_cols

    if fill_numeric_missing:
        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            missing_count = int(cleaned_df[col].isna().sum())
            if missing_count > 0:
                median_value = cleaned_df[col].median()
                cleaned_df[col] = cleaned_df[col].fillna(median_value)
                summary["numeric_filled"][col] = {
                    "filled_count": missing_count,
                    "fill_value": float(median_value) if pd.notna(median_value) else None,
                }

    if fill_categorical_missing:
        categorical_cols = cleaned_df.select_dtypes(exclude=[np.number]).columns
        for col in categorical_cols:
            missing_count = int(cleaned_df[col].isna().sum())
            if missing_count > 0:
                mode_series = cleaned_df[col].mode(dropna=True)
                fill_value = mode_series.iloc[0] if not mode_series.empty else "Unknown"
                cleaned_df[col] = cleaned_df[col].fillna(fill_value)
                summary["categorical_filled"][col] = {
                    "filled_count": missing_count,
                    "fill_value": str(fill_value),
                }

    summary["final_shape"] = cleaned_df.shape
    return cleaned_df, summary
