from __future__ import annotations

import pandas as pd
import plotly.express as px


def plot_histogram(df: pd.DataFrame, column: str):
    return px.histogram(df, x=column, title=f"Distribution of {column}")


def plot_bar(df: pd.DataFrame, column: str):
    counts = (
        df[column]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(15)
        .reset_index()
    )
    counts.columns = [column, "count"]
    return px.bar(counts, x=column, y="count", title=f"Top Categories in {column}")


def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str):
    return px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")


def plot_box(df: pd.DataFrame, cat_col: str, num_col: str):
    plot_df = df[[cat_col, num_col]].copy()
    plot_df[cat_col] = plot_df[cat_col].fillna("Missing").astype(str)
    top_cats = plot_df[cat_col].value_counts().head(10).index
    plot_df = plot_df[plot_df[cat_col].isin(top_cats)]
    return px.box(plot_df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")


def plot_heatmap(df: pd.DataFrame, columns: list[str]):
    corr = df[columns].corr(numeric_only=True)
    return px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")
