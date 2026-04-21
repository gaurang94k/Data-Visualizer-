from __future__ import annotations

from itertools import combinations
import pandas as pd


def generate_insights(df: pd.DataFrame, profile: dict, column_groups: dict) -> list[str]:
    insights: list[str] = []

    # missing values
    missing_df = profile["missing_summary"]
    for _, row in missing_df.head(3).iterrows():
        if row["missing_count"] > 0:
            insights.append(
                f"'{row['column']}' has {int(row['missing_count']):,} missing values ({row['missing_pct']}%)."
            )

    # duplicates
    if profile["duplicate_rows"] > 0:
        insights.append(f"The dataset contains {profile['duplicate_rows']:,} duplicate rows.")

    # dominant categories
    for col in (column_groups["categorical"] + column_groups["text"])[:3]:
        series = df[col].dropna().astype(str)
        if len(series) == 0:
            continue
        top_value = series.value_counts().idxmax()
        top_count = int(series.value_counts().max())
        pct = round((top_count / len(series)) * 100, 2)
        insights.append(f"In '{col}', the most common value is '{top_value}' ({pct}% of non-missing rows).")

    # strongest correlations
    numeric_cols = column_groups["numeric"]
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True)
        pairs = []
        for x, y in combinations(numeric_cols, 2):
            value = corr.loc[x, y]
            if pd.notna(value):
                pairs.append(((x, y), float(value)))
        if pairs:
            pair, value = max(pairs, key=lambda item: abs(item[1]))
            direction = "positive" if value >= 0 else "negative"
            insights.append(
                f"The strongest numeric relationship is between '{pair[0]}' and '{pair[1]}' with a {direction} correlation of {value:.2f}."
            )

    # skewness and outliers
    for col in numeric_cols[:3]:
        series = df[col].dropna()
        if len(series) < 5:
            continue
        skew = float(series.skew())
        if skew > 1:
            insights.append(f"'{col}' is positively skewed, with a tail toward higher values.")
        elif skew < -1:
            insights.append(f"'{col}' is negatively skewed, with a tail toward lower values.")

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = int(((series < lower) | (series > upper)).sum())
            if outliers > 0:
                insights.append(f"'{col}' contains {outliers:,} potential outliers based on the IQR rule.")

    # keep concise
    seen = set()
    deduped = []
    for item in insights:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped[:10]
