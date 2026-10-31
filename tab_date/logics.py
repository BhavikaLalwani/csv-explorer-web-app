import pandas as pd


def analyse_datetime(series):
    # Convert the selected column to datetime
    dates = pd.to_datetime(series, errors="coerce")
    valid_dates = dates.dropna()

    today = pd.Timestamp.today().normalize()

    # Calculate datetime statistics
    summary = {
        "Number of Unique Values": dates.nunique(),
        "Number of Rows with Missing Values": dates.isna().sum(),
        "Minimum Value": valid_dates.min() if not valid_dates.empty else None,
        "Maximum Value": valid_dates.max() if not valid_dates.empty else None,
        "Number of Weekend Dates": (valid_dates.dt.dayofweek >= 5).sum(),
        "Number of Weekday Dates": (valid_dates.dt.dayofweek < 5).sum(),
        "Number of Dates in Future": (
            valid_dates.dt.normalize() > today
        ).sum(),
        "Number of Rows with 1900-01-01": (
            valid_dates.dt.normalize() == pd.Timestamp("1900-01-01")
        ).sum(),
        "Number of Rows with 1970-01-01": (
            valid_dates.dt.normalize() == pd.Timestamp("1970-01-01")
        ).sum(),
    }

    # Create a static summary table
    summary_df = pd.DataFrame(
        list(summary.items()),
        columns=["Description", "Value"]
    )

    # Calculate top 20 most frequent dates
    counts = valid_dates.value_counts().head(20)

    frequency_df = pd.DataFrame({
        "Value": counts.index.astype(str),
        "Occurrence": counts.values,
       "Percentage (%)": (counts.values / len(valid_dates) * 100).round(2)
    })

    return summary_df, frequency_df, dates

