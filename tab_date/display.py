import streamlit as st
import pandas as pd
import altair as alt

from tab_date.logics import analyse_datetime


def show_datetime_tab(df):
    st.subheader("Datetime Serie")

    # Detect datetime columns
    datetime_columns = df.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns.tolist()

    # If no datetime columns, use text columns
    if datetime_columns:
        columns = datetime_columns
    else:
        columns = df.select_dtypes(
            include=["object", "string"]
        ).columns.tolist()

    if not columns:
        st.warning("No datetime or text columns available.")
        return

    # Date column selection
    selected = st.selectbox(
        "Which datetime column do you want to explore?",
        columns
    )

    # Get results from logics.py
    summary, frequency, dates = analyse_datetime(df[selected])

    # Display statistics
    st.write("### Date Column")
    st.table(summary)

    # Create interactive histogram
    st.write("### Date Histogram")

    valid_dates = dates.dropna()

    if not valid_dates.empty:
        date_counts = (
            valid_dates.dt.normalize()
            .value_counts()
            .sort_index()
        )

        chart_df = pd.DataFrame({
            "Date": date_counts.index.strftime("%Y-%m-%d"),
            "Count": date_counts.values
        })

            
        chart = alt.Chart(chart_df).mark_bar().encode(
            x=alt.X(
                "Date:N",
                title="Date",
                sort=None,
                axis=alt.Axis(labelAngle=-45)
            ),
            y=alt.Y("Count:Q", title="Count"),
            tooltip=["Date:N", "Count:Q"]
        )

        st.altair_chart(chart, use_container_width=True)


    else:
        st.info("No valid dates found.")

    # Display most frequent values
    st.write("### Most Frequent Values")
    st.dataframe(frequency, use_container_width=True)
