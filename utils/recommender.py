from __future__ import annotations

from itertools import combinations
import pandas as pd


def recommend_charts(df: pd.DataFrame, column_groups: dict) -> dict:
    numeric_cols = column_groups["numeric"]
    categorical_cols = column_groups["categorical"] + column_groups["text"]

    histograms = numeric_cols[:3]

    bars = []
    for col in categorical_cols:
        nunique = df[col].nunique(dropna=True)
        if 1 < nunique <= 30:
            bars.append(col)
        if len(bars) >= 3:
            break

    scatters = []
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True).abs()
        pairs = []
        for x, y in combinations(numeric_cols, 2):
            score = corr.loc[x, y]
            if pd.notna(score):
                pairs.append(((x, y), float(score)))
        pairs.sort(key=lambda item: item[1], reverse=True)
        scatters = [pair for pair, _ in pairs[:3]]

    boxes = []
    for cat in column_groups["categorical"]:
        if df[cat].nunique(dropna=True) <= 15:
            for num in numeric_cols[:2]:
                boxes.append((cat, num))
                if len(boxes) >= 2:
                    break
        if len(boxes) >= 2:
            break

    heatmap = numeric_cols if len(numeric_cols) >= 2 else []

    return {
        "histograms": histograms,
        "bars": bars,
        "scatters": scatters,
        "boxes": boxes,
        "heatmap": heatmap,
    }
