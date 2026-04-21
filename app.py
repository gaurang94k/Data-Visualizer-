import streamlit as st

from utils.loader import load_uploaded_file
from utils.profiler import profile_dataframe, split_columns_by_type
from utils.recommender import recommend_charts
from utils.charts import (
    plot_histogram,
    plot_bar,
    plot_scatter,
    plot_box,
    plot_heatmap,
)
from utils.insights import generate_insights
from utils.cleaner import basic_clean_data

st.set_page_config(page_title="InsightLens - Smart Data Visualizer", layout="wide")

st.title("InsightLens: Smart Data Visualizer")
st.write(
    "Upload a CSV file to automatically profile the dataset, generate recommended charts, and surface key insights."
)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file to begin.")
    st.stop()

try:
    df = load_uploaded_file(uploaded_file)
except Exception as exc:
    st.error(f"Could not read file: {exc}")
    st.stop()

if df.empty:
    st.warning("The uploaded file is empty.")
    st.stop()

st.header("1. Basic Cleaning Options")
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
    drop_empty_rows = st.checkbox("Drop fully empty rows", value=True)
with col_c2:
    drop_empty_columns = st.checkbox("Drop fully empty columns", value=True)
    fill_numeric_missing = st.checkbox("Fill missing numeric values with median", value=False)
with col_c3:
    fill_categorical_missing = st.checkbox("Fill missing categorical values with mode", value=False)

if st.button("Apply Basic Cleaning"):
    df, cleaning_summary = basic_clean_data(
        df,
        remove_duplicates=remove_duplicates,
        drop_empty_rows=drop_empty_rows,
        drop_empty_columns=drop_empty_columns,
        fill_numeric_missing=fill_numeric_missing,
        fill_categorical_missing=fill_categorical_missing,
    )

    st.success("Basic cleaning applied.")
    with st.expander("Cleaning Summary", expanded=True):
        st.write(f"Original shape: {cleaning_summary['original_shape']}")
        st.write(f"Final shape: {cleaning_summary['final_shape']}")
        st.write(f"Duplicates removed: {cleaning_summary['duplicates_removed']}")
        st.write(f"Fully empty rows removed: {cleaning_summary['empty_rows_removed']}")
        st.write(f"Fully empty columns removed: {cleaning_summary['empty_columns_removed']}")
        if cleaning_summary["numeric_filled"]:
            st.write("#### Numeric columns filled")
            st.json(cleaning_summary["numeric_filled"])
        if cleaning_summary["categorical_filled"]:
            st.write("#### Categorical columns filled")
            st.json(cleaning_summary["categorical_filled"])

profile = profile_dataframe(df)
column_groups = split_columns_by_type(df)
recommendations = recommend_charts(df, column_groups)
insights = generate_insights(df, profile, column_groups)

st.header("2. Dataset Preview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", f"{profile['n_rows']:,}")
col2.metric("Columns", f"{profile['n_columns']:,}")
col3.metric("Duplicate Rows", f"{profile['duplicate_rows']:,}")
col4.metric("Missing Cells", f"{profile['total_missing']:,}")

st.dataframe(df.head(20), use_container_width=True)

st.header("3. Dataset Overview")
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Column Types")
    st.write(
        {
            "numeric": len(column_groups["numeric"]),
            "categorical": len(column_groups["categorical"]),
            "datetime": len(column_groups["datetime"]),
            "text": len(column_groups["text"]),
        }
    )

    st.subheader("Missing Values")
    st.dataframe(profile["missing_summary"], use_container_width=True)

with col_b:
    st.subheader("Unique Counts")
    st.dataframe(profile["unique_summary"], use_container_width=True)

    st.subheader("Numeric Summary")
    if not profile["numeric_summary"].empty:
        st.dataframe(profile["numeric_summary"], use_container_width=True)
    else:
        st.info("No numeric columns found.")

st.header("4. Recommended Charts")

if recommendations["heatmap"]:
    st.subheader("Correlation Heatmap")
    st.plotly_chart(
        plot_heatmap(df, recommendations["heatmap"]),
        use_container_width=True,
        key="heatmap"
    )

if recommendations["histograms"]:
    st.subheader("Numeric Distributions")
    for col in recommendations["histograms"]:
        st.plotly_chart(
            plot_histogram(df, col),
            use_container_width=True,
            key=f"hist_{col}"
        )

if recommendations["bars"]:
    st.subheader("Top Categories")
    for col in recommendations["bars"]:
        st.plotly_chart(
            plot_bar(df, col),
            use_container_width=True,
            key=f"bar_{col}"
        )

if recommendations["scatters"]:
    st.subheader("Numeric Relationships")
    for x_col, y_col in recommendations["scatters"]:
        st.plotly_chart(
            plot_scatter(df, x_col, y_col),
            use_container_width=True,
            key=f"scatter_{x_col}_{y_col}"
        )

if recommendations["boxes"]:
    st.subheader("Numeric vs Category")
    for cat_col, num_col in recommendations["boxes"]:
        st.plotly_chart(
            plot_box(df, cat_col, num_col),
            use_container_width=True,
            key=f"box_{cat_col}_{num_col}"
        )

st.header("5. Key Insights")
if insights:
    for item in insights:
        st.markdown(f"- {item}")
else:
    st.info("No major insights were generated for this dataset.")

st.header("6. Manual Exploration")
chart_type = st.selectbox("Choose a chart type", ["Histogram", "Bar", "Scatter", "Box"])

if chart_type == "Histogram":
    numeric_cols = column_groups["numeric"]
    if numeric_cols:
        selected = st.selectbox("Numeric column", numeric_cols)
        st.plotly_chart(
            plot_histogram(df, selected),
            use_container_width=True,
            key=f"manual_hist_{selected}"
        )
    else:
        st.info("No numeric columns available.")

elif chart_type == "Bar":
    categorical_cols = column_groups["categorical"] + column_groups["text"]
    if categorical_cols:
        selected = st.selectbox("Categorical column", categorical_cols)
        st.plotly_chart(
            plot_bar(df, selected),
            use_container_width=True,
            key=f"manual_bar_{selected}"
        )
    else:
        st.info("No categorical columns available.")

elif chart_type == "Scatter":
    numeric_cols = column_groups["numeric"]
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        st.plotly_chart(
            plot_scatter(df, x_col, y_col),
            use_container_width=True,
            key=f"manual_scatter_{x_col}_{y_col}"
        )
    else:
        st.info("At least two numeric columns are needed.")

elif chart_type == "Box":
    categorical_cols = column_groups["categorical"]
    numeric_cols = column_groups["numeric"]
    if categorical_cols and numeric_cols:
        x_col = st.selectbox("Category column", categorical_cols, key="box_x")
        y_col = st.selectbox("Numeric column", numeric_cols, key="box_y")
        st.plotly_chart(
            plot_box(df, x_col, y_col),
            use_container_width=True,
            key=f"manual_box_{x_col}_{y_col}"
        )
    else:
        st.info("This chart needs both categorical and numeric columns.")