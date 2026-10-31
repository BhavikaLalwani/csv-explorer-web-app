import pandas as pd

from tab_text.logics import (
    get_text_columns,
    calculate_text_stats,
    calculate_frequent_text_values
)


def test_get_text_columns():
    df = pd.DataFrame({
        "Review": ["Good", "Bad", "Excellent"],
        "Rating": [5, 1, 4]
    })

    result = get_text_columns(df)

    assert result == ["Review"]


def test_calculate_text_stats():
    df = pd.DataFrame({
        "Review": ["Good", "Excellent", "Good", None]
    })

    result = calculate_text_stats(df, "Review")

    stats = dict(zip(
        result["Description"],
        result["Value"]
    ))

    assert stats["Number of Unique Values"] == 2
    assert stats["Number of Rows with Missing Values"] == 1
    assert stats["Number of Empty Strings"] == 0
    assert round(stats["Average Text Length"], 2) == 5.67
    assert stats["Minimum Text Length"] == 4
    assert stats["Maximum Text Length"] == 9


def test_calculate_frequent_text_values():
    df = pd.DataFrame({
        "Review": ["Good", "Excellent", "Good", None]
    })

    result = calculate_frequent_text_values(df, "Review")

    assert result.iloc[0]["value"] == "Good"
    assert result.iloc[0]["occurrence"] == 2
    assert result.iloc[0]["percentage"] == 0.5


def test_empty_text_column():
    df = pd.DataFrame({
        "Review": pd.Series([None, None], dtype="string")
    })

    stats = calculate_text_stats(df, "Review")
    frequency = calculate_frequent_text_values(df, "Review")

    values = dict(zip(stats["Description"], stats["Value"]))

    assert values["Number of Unique Values"] == 0
    assert values["Number of Rows with Missing Values"] == 2
    assert values["Average Text Length"] == 0
    assert frequency.empty