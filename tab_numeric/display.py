
import streamlit as st
import altair as alt
import pandas as pd

from tab_numeric.logics import (
    get_numeric_columns,
    calculate_numeric_stats,
    calculate_frequent_values
)


def display_numeric_tab(df):
    """Display numeric statistics, a histogram, and frequent values."""

    st.subheader("Numeric Serie")

    # Find numeric columns in the uploaded dataset
    numeric_columns = get_numeric_columns(df)

    if not numeric_columns:
        st.warning("No numeric columns found in the dataset.")
        return

    # Select a numeric column
    selected_column = st.selectbox(
        "Which numeric column do you want to explore?",
        numeric_columns
    )

    # Calculate and display statistics
    stats = calculate_numeric_stats(df, selected_column)

    count_metrics = {
        "Number of Unique Values",
        "Number of Rows with Missing Values",
        "Number of Rows with 0",
        "Number of Rows with Negative Values"
    }

    stats["Value"] = [
        f"{int(value):,}" if description in count_metrics
        else "N/A" if pd.isna(value)
        else f"{value:,.4f}"
        for description, value in zip(
            stats["Description"], stats["Value"]
        )
    ]

    st.table(stats)

    # Remove missing values before creating the histogram
    histogram_data = (
        df[[selected_column]]
        .dropna()
        .rename(columns={selected_column: "numeric_value"})
    )

    st.subheader("Histogram")

    if histogram_data.empty:
        st.info("No valid numeric values available for the histogram.")
    else:
        if histogram_data["numeric_value"].nunique() == 1:
            st.info("All values in this column are identical.")

        histogram = alt.Chart(histogram_data).mark_bar().encode(
            x=alt.X(
                "numeric_value:Q",
                bin=alt.Bin(maxbins=30),
                title=f"{selected_column} (binned)"
            ),
            y=alt.Y(
                "count():Q",
                title="Count of Records"
            ),
            tooltip=[
                alt.Tooltip("count():Q", title="Records")
            ]
        )

        st.altair_chart(histogram, use_container_width=True)

    # Display the 20 most frequent numeric values
    st.subheader("Most Frequent Values")

    frequent_values = calculate_frequent_values(
        df, selected_column
    )

    if frequent_values.empty:
        st.info("No values available to display.")
    else:
        st.dataframe(
            frequent_values,
            hide_index=True,
            column_config={
                "percentage": st.column_config.NumberColumn(
                    "percentage",
                    format="%.4f"
                )
            }
        )
