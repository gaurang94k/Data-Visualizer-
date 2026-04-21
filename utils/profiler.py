from __future__ import annotations

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype


def split_columns_by_type(df: pd.DataFrame) -> dict:
    numeric = []
    categorical = []
    datetime_cols = []
    text = []

    for col in df.columns:
        series = df[col]
        non_null = series.dropna()
        nunique = non_null.nunique()

        if is_datetime64_any_dtype(series):
            datetime_cols.append(col)
        elif is_numeric_dtype(series):
            numeric.append(col)
        elif len(non_null) > 0 and _looks_like_datetime(non_null):
            datetime_cols.append(col)
        elif nunique <= 30:
            categorical.append(col)
        else:
            text.append(col)

    return {
        "numeric": numeric,
        "categorical": categorical,
        "datetime": datetime_cols,
        "text": text,
    }


def profile_dataframe(df: pd.DataFrame) -> dict:
    missing_counts = df.isna().sum().sort_values(ascending=False)
    missing_pct = (df.isna().mean() * 100).round(2)
    missing_summary = pd.DataFrame({
        "column": df.columns,
        "missing_count": [int(missing_counts.get(col, 0)) for col in df.columns],
        "missing_pct": [float(missing_pct.get(col, 0.0)) for col in df.columns],
    }).sort_values(["missing_count", "column"], ascending=[False, True]).reset_index(drop=True)

    unique_summary = pd.DataFrame({
        "column": df.columns,
        "unique_count": [int(df[col].nunique(dropna=True)) for col in df.columns],
    }).sort_values(["unique_count", "column"], ascending=[False, True]).reset_index(drop=True)

    numeric_summary = df.select_dtypes(include="number").describe().T.reset_index().rename(columns={"index": "column"})

    return {
        "n_rows": int(df.shape[0]),
        "n_columns": int(df.shape[1]),
        "duplicate_rows": int(df.duplicated().sum()),
        "total_missing": int(df.isna().sum().sum()),
        "missing_summary": missing_summary,
        "unique_summary": unique_summary,
        "numeric_summary": numeric_summary,
    }


def _looks_like_datetime(series: pd.Series) -> bool:
    sample = series.astype(str).head(20)
    try:
        parsed = pd.to_datetime(sample, errors="coerce")
        return parsed.notna().mean() >= 0.7
    except Exception:
        return False
