import pandas as pd


def get_text_columns(df):
    """Identify all text columns in the CSV file."""

    return df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()


def calculate_text_stats(df, column):
    """Calculate statistics for the selected text column."""

    series = df[column]

    # Remove missing values for text-length calculations
    valid_text = series.dropna().astype(str)

    # Calculate the length of each text value
    text_lengths = valid_text.str.len()

    stats = {
        "Number of Unique Values": series.nunique(),

        "Number of Rows with Missing Values": series.isna().sum(),

        "Number of Empty Strings": (
            valid_text.str.strip() == ""
        ).sum(),

        "Average Text Length": (
            text_lengths.mean()
            if not text_lengths.empty else 0
        ),

        "Minimum Text Length": (
            text_lengths.min()
            if not text_lengths.empty else 0
        ),

        "Maximum Text Length": (
            text_lengths.max()
            if not text_lengths.empty else 0
        )
    }

    return pd.DataFrame(
        stats.items(),
        columns=["Description", "Value"]
    )


def calculate_frequent_text_values(df, column):
    """Calculate the 20 most frequently occurring text values."""

    series = df[column]

    frequency = (
        series.value_counts()
        .head(20)
        .rename_axis("value")
        .reset_index(name="occurrence")
    )

    frequency["percentage"] = (
        frequency["occurrence"] / len(series)
        if len(series) > 0 else 0.0
    )

    return frequency