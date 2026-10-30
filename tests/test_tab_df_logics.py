# Automated tests for tab_df/logics.py.
# Run them from the project folder with:  python -m pytest tests -v

import io

import numpy as np
import pandas as pd
import pytest

from tab_df.logics import EXPLORATION_METHODS, Dataset, format_bytes, simple_type


# A tiny made-up table where we already know the answers:
# 6 rows, 1 duplicate (Ann appears twice), and 2 rows with an empty cell.
@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["Ann", "Bob", "Cat", "Ann", None, "Dan"],
            "age": [30, 25, np.nan, 30, 40, 35],
            "joined": ["2024-01-05", "2024-02-10", "2024-03-15", "2024-01-05", "2024-04-20", "2024-05-25"],
        }
    )


@pytest.fixture
def dataset(sample_df: pd.DataFrame) -> Dataset:
    return Dataset.from_dataframe(sample_df, name="sample.csv")


# Pretends to be a file uploaded through Streamlit.
def _csv_bytes(text: str, encoding: str = "utf-8") -> io.BytesIO:
    return io.BytesIO(text.encode(encoding))


# Does reading a CSV work, including awkward files?
class TestLoading:
    def test_loads_utf8_csv(self):
        ds = Dataset(_csv_bytes("a,b\n1,x\n2,y\n"))
        assert ds.get_n_rows() == 2
        assert ds.get_n_cols() == 2

    def test_falls_back_to_latin1(self):
        ds = Dataset(_csv_bytes("city\nSão Paulo\nMontréal\n", encoding="latin-1"))
        assert ds.df["city"].tolist() == ["São Paulo", "Montréal"]

    @pytest.mark.parametrize("content", ["", "\n\n"])
    def test_empty_file_raises_clear_error(self, content):
        with pytest.raises(ValueError, match="empty"):
            Dataset(_csv_bytes(content))

    def test_from_dataframe_keeps_data_and_name(self, sample_df):
        ds = Dataset.from_dataframe(sample_df, name="x.csv")
        assert ds.df is sample_df
        assert ds.name == "x.csv"

    def test_no_data_is_detected(self):
        assert Dataset().is_df_none()
        assert Dataset.from_dataframe(pd.DataFrame()).is_df_none()


# Are the numbers in the summary table correct?
class TestSummary:
    def test_counts(self, dataset):
        assert dataset.get_n_rows() == 6
        assert dataset.get_n_cols() == 3
        assert dataset.get_n_duplicates() == 1
        assert dataset.get_n_missing() == 2

    def test_summary_table_layout(self, dataset):
        summary = dataset.get_summary_df()
        assert list(summary.columns) == ["Description", "Value"]
        assert summary["Value"].tolist() == [6, 3, 1, 2]

    def test_empty_dataset_returns_zeros(self):
        assert Dataset().get_summary_df()["Value"].tolist() == [0, 0, 0, 0]


# Is the column information (type, memory, % missing) correct?
class TestColumns:
    def test_cols_dtype_lists_every_column_then_index(self, dataset):
        table = dataset.get_cols_dtype()
        assert table["column"].tolist() == ["name", "age", "joined", "Index"]
        assert (table["memory"] > 0).all()

    def test_column_profile_types(self, dataset):
        profile = dataset.get_column_profile().set_index("Column")
        assert profile.loc["name", "Type"] == "Text"
        assert profile.loc["age", "Type"] == "Numeric"
        assert profile.loc["joined", "Type"] == "Date"

    def test_column_profile_missing_percentage(self, dataset):
        profile = dataset.get_column_profile().set_index("Column")
        assert profile.loc["age", "Missing %"] == "16.7%"
        assert profile.loc["joined", "Missing %"] == "0.0%"

    def test_type_counts(self, dataset):
        assert dataset.get_type_counts() == {"Text": 1, "Numeric": 1, "Date": 1}


# Does each kind of column get the right label?
class TestSimpleType:
    @pytest.mark.parametrize(
        "values, expected",
        [
            ([1, 2, 3], "Numeric"),
            ([1.5, None, 2.0], "Numeric"),
            ([True, False], "Boolean"),
            (["2024-01-01", "2024-12-31"], "Date"),
            (["apple", "banana"], "Text"),
            (["2024", "2025"], "Text"),
            ([None, None], "Text"),
            (["", "  "], "Text"),
        ],
    )
    def test_classification(self, values, expected):
        assert simple_type(pd.Series(values)) == expected

    def test_real_datetime_dtype(self):
        assert simple_type(pd.Series(pd.to_datetime(["2024-01-01"]))) == "Date"


# Are byte sizes turned into readable text correctly?
class TestFormatBytes:
    @pytest.mark.parametrize(
        "n_bytes, expected",
        [(0, "0 B"), (512, "512 B"), (2048, "2.0 KB"), (5 * 1024**2, "5.0 MB"), (3 * 1024**3, "3.0 GB")],
    )
    def test_format(self, n_bytes, expected):
        assert format_bytes(n_bytes) == expected


# Do Head, Tail and Sample return the right rows?
class TestRows:
    def test_head_and_tail(self, dataset):
        assert dataset.get_rows(2, "Head").index.tolist() == [0, 1]
        assert dataset.get_rows(2, "Tail").index.tolist() == [4, 5]

    def test_sample_size_and_reproducibility(self, dataset):
        first = dataset.get_rows(3, "Sample", random_state=42)
        second = dataset.get_rows(3, "Sample", random_state=42)
        assert len(first) == 3
        assert first.equals(second)

    def test_sample_larger_than_dataset_is_capped(self, dataset):
        assert len(dataset.get_rows(50, "Sample")) == 6

    @pytest.mark.parametrize("method", EXPLORATION_METHODS)
    def test_every_method_works(self, dataset, method):
        assert len(dataset.get_rows(4, method)) == 4

    def test_unknown_method_raises(self, dataset):
        with pytest.raises(ValueError, match="Unknown exploration method"):
            dataset.get_rows(5, "Middle")

    def test_no_data_returns_empty_frame(self):
        assert Dataset().get_rows(5, "Head").empty
