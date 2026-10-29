
import streamlit as st
import pandas as pd

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
        tab1, tab2, tab3, tab4 = st.tabs([
            "DataFrame",
            "Numeric Serie",
            "Text Serie",
            "Datetime Serie"
        ])

        with tab1:
            st.info("DataFrame analysis coming soon.")

        with tab2:
            st.info("Numeric analysis coming soon.")

        with tab3:
            st.info("Text analysis coming soon.")

        with tab4:
            st.info("Datetime analysis coming soon.")
