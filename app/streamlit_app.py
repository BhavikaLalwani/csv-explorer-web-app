import sys
from pathlib import Path

# The tab_* folders sit next to app/, not inside it.
# This line lets Python find them when we run: streamlit run app/streamlit_app.py
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from tab_df.display import display_df_tab
from tab_numeric.display import display_numeric_tab
from tab_date.display import show_datetime_tab

# Page title and full-width layout
st.set_page_config(
    page_title="CSV Explorer",
    layout="wide"
)

st.title("CSV Explorer")

# Upload section
with st.expander(
    "Streamlit application for performing data exploration on a CSV",
    expanded=True
):
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"]
    )

# Only show the tabs once a CSV has been uploaded
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

    except Exception as e:
        st.error(f"Unable to read CSV file: {e}")

    else:
        tab_df, tab_numeric, tab_text, tab_datetime = st.tabs([
            "DataFrame",
            "Numeric Serie",
            "Text Serie",
            "Datetime Serie"
        ])

        with tab_df:
            display_df_tab(df, uploaded_file.name)

        with tab_numeric:
            display_numeric_tab(df)

        with tab_text:
            st.info("Text analysis coming soon.")

        with tab_datetime:
            show_datetime_tab(df)
