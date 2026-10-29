import pandas as pd


def get_numeric_columns(df):
    """Get all numeric columns from the dataset."""
    return df.select_dtypes(include="number").columns.tolist()


def calculate_numeric_stats(df, column):
    """Calculate the required statistics for a numeric column."""
    series = df[column]

    stats = {
        "Number of Unique Values": series.nunique(),
        "Number of Rows with Missing Values": series.isna().sum(),
        "Number of Rows with 0": (series == 0).sum(),
        "Number of Rows with Negative Values": (series < 0).sum(),
        "Average Value": series.mean(),
        "Standard Deviation Value": series.std(),
        "Minimum Value": series.min(),
        "Maximum Value": series.max(),
        "Median Value": series.median()
    }

    return pd.DataFrame(
        stats.items(),
        columns=["Description", "Value"]
    )


def calculate_frequent_values(df, column):
    """Get the 20 most frequent values and their percentages."""
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
