import sys
from pathlib import Path

# Let Python find the tab_* folders, which sit next to app/.
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402
import pandas as pd  # noqa: E402
from tab_df.display import display_df_tab  # noqa: E402
from tab_numeric.display import display_numeric_tab  # noqa: E402

# Configure the application
st.set_page_config(
    page_title="CSV Explorer",
    layout="wide"
)

st.title("CSV Explorer")

# Upload a CSV file
with st.expander(
    "Streamlit application for performing data exploration on a CSV",
    expanded=True
):
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"]
    )

# Display the four tabs after uploading a CSV
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
            st.info("Datetime analysis coming soon.")
