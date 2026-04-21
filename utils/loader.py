import pandas as pd


def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Load an uploaded CSV file into a DataFrame."""
    return pd.read_csv(uploaded_file)
