# InsightLens: Smart Data Visualizer

InsightLens is a Streamlit app that automatically profiles an uploaded CSV dataset, recommends useful charts, and generates rule-based insights.

## Features

- CSV upload
- Basic optional cleaning
  - remove duplicate rows
  - drop fully empty rows and columns
  - fill missing numeric values with median
  - fill missing categorical values with mode
- Dataset preview and profiling
- Automatic chart recommendations
  - histogram
  - bar chart
  - scatter plot
  - box plot
  - correlation heatmap
- Rule-based insights for missing data, duplicates, category dominance, skewness, outliers, and correlations
- Manual exploration panel

## Project structure

```text
smart_data_visualizer/
│
├── app.py
├── requirements.txt
├── README.md
└── utils/
    ├── __init__.py
    ├── loader.py
    ├── profiler.py
    ├── recommender.py
    ├── charts.py
    ├── insights.py
    └── cleaner.py
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

This project can be deployed directly on Streamlit Community Cloud by connecting a GitHub repository and selecting `app.py` as the entry point.
