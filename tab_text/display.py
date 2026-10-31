import streamlit as st
import altair as alt

from tab_text.logics import (
    get_text_columns,
    calculate_text_stats,
    calculate_frequent_text_values
)


def display_text_analysis(df):

    st.header("Text Column Analysis")

    # Identify available text columns
    text_columns = get_text_columns(df)

    if not text_columns:
        st.warning("No text columns found in the uploaded CSV.")
        return

    # Allow user to select a text column
    selected_column = st.selectbox(
        "Select a text column to analyze:",
        text_columns
    )

    # Analyze button
    if st.button("Analyze Text Column"):

        # Calculate statistics
        stats = calculate_text_stats(df, selected_column)

        # Calculate frequent values
        frequency = calculate_frequent_text_values(
            df, selected_column
        )

        # Display statistics
        st.subheader("Text Column Statistics")

        st.dataframe(
            stats,
            use_container_width=True,
            hide_index=True
        )

        # Display frequency table
        st.subheader("Top 20 Most Frequent Text Values")

        st.dataframe(
            frequency,
            use_container_width=True,
            hide_index=True
        )

        # Display frequency chart
        st.subheader("Frequency Distribution")

        if not frequency.empty:

            chart = alt.Chart(frequency).mark_bar().encode(
                x=alt.X(
                    "occurrence:Q",
                    title="Number of Occurrences"
                ),
                y=alt.Y(
                    "value:N",
                    sort="-x",
                    title="Text Value"
                ),
                tooltip=[
                    "value",
                    "occurrence",
                    "percentage"
                ]
            ).properties(
                height=400
            )

            st.altair_chart(
                chart,
                use_container_width=True
            )

        else:
            st.info("No non-missing text values available.")