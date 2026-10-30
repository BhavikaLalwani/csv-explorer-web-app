"""Logic for the DataFrame tab.

This module contains no Streamlit code, so every calculation here can be
imported and tested on its own. The display module (``tab_df/display.py``)
calls these methods and only takes care of rendering the results.
"""

import warnings
from typing import IO, Optional, Union

import pandas as pd
from pandas.api import types as ptypes

# Share of non-empty values that must parse as dates for a text column to
# be labelled "Date".
_DATE_PARSE_THRESHOLD = 0.9
# Number of values checked when guessing whether a text column holds dates.
_DATE_SAMPLE_SIZE = 200

# Options offered by the exploration radio button, in display order.
EXPLORATION_METHODS = ("Head", "Tail", "Sample")

# Encodings tried, in order, when reading an uploaded CSV.
_ENCODINGS = ("utf-8", "latin-1")


class Dataset:
    """Holds a loaded CSV and computes the overview shown in the DataFrame tab.

    Attributes:
        name: Name of the uploaded file (for display only).
        df: The loaded data, or ``None`` if nothing has been loaded yet.
    """

    def __init__(self, file: Optional[Union[str, IO]] = None, name: str = "") -> None:
        self.name = name
        self.df: Optional[pd.DataFrame] = None
        if file is not None:
            self.set_data(file)

    # ------------------------------------------------------------------ #
    # Loading
    # ------------------------------------------------------------------ #
    def set_data(self, file: Union[str, IO]) -> None:
        """Read a CSV file (path or file-like object) into ``self.df``.

        Tries UTF-8 first, then Latin-1, so files exported from Excel on
        Windows still load.

        Raises:
            ValueError: If the file is empty, has no columns, or cannot be
                parsed as CSV.
        """
        last_error: Optional[Exception] = None
        for encoding in _ENCODINGS:
            if hasattr(file, "seek"):
                file.seek(0)  # rewind before every attempt
            try:
                self.df = pd.read_csv(file, encoding=encoding)
                return
            except UnicodeDecodeError as error:
                last_error = error
            except pd.errors.EmptyDataError as error:
                raise ValueError("The file is empty or has no columns.") from error
            except pd.errors.ParserError as error:
                raise ValueError(f"The file could not be parsed as CSV: {error}") from error
        raise ValueError(f"Could not decode the file: {last_error}")

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, name: str = "") -> "Dataset":
        """Wrap a DataFrame that has already been loaded elsewhere."""
        dataset = cls(name=name)
        dataset.df = df
        return dataset

    def is_df_none(self) -> bool:
        """Return True if no data has been loaded (or it is empty)."""
        return self.df is None or self.df.empty

    # ------------------------------------------------------------------ #
    # Summary statistics
    # ------------------------------------------------------------------ #
    def get_n_rows(self) -> int:
        """Number of rows in the dataset."""
        return 0 if self.df is None else int(self.df.shape[0])

    def get_n_cols(self) -> int:
        """Number of columns in the dataset."""
        return 0 if self.df is None else int(self.df.shape[1])

    def get_n_duplicates(self) -> int:
        """Number of rows that are exact duplicates of an earlier row."""
        return 0 if self.df is None else int(self.df.duplicated().sum())

    def get_n_missing(self) -> int:
        """Number of rows containing at least one missing value."""
        return 0 if self.df is None else int(self.df.isna().any(axis=1).sum())

    def get_summary_df(self) -> pd.DataFrame:
        """Return the overview table (Description / Value)."""
        return pd.DataFrame(
            {
                "Description": [
                    "Number of Rows",
                    "Number of Columns",
                    "Number of Duplicated Rows",
                    "Number of Rows with Missing Values",
                ],
                "Value": [
                    self.get_n_rows(),
                    self.get_n_cols(),
                    self.get_n_duplicates(),
                    self.get_n_missing(),
                ],
            }
        )

    def get_cols_dtype(self) -> pd.DataFrame:
        """Return one row per column with its data type and memory usage.

        Memory is reported in bytes by ``DataFrame.memory_usage``, which also
        includes a row for the Index (it has no data type, so it shows
        ``nan``), matching the reference screenshot in the brief.
        """
        if self.df is None:
            return pd.DataFrame(columns=["column", "data_type", "memory"])

        memory = self.df.memory_usage(index=True, deep=False)
        dtypes = self.df.dtypes.reindex(memory.index)  # Index -> NaN
        table = pd.DataFrame(
            {
                "column": memory.index.astype(str),
                "data_type": dtypes.astype(str).values,
                "memory": memory.values,
            }
        )
        # Put the Index row last, as in the brief.
        is_index = table["column"] == "Index"
        return pd.concat([table[~is_index], table[is_index]], ignore_index=True)

    def get_total_memory(self) -> int:
        """Total memory used by the data and its index, in bytes."""
        return 0 if self.df is None else int(self.df.memory_usage(index=True).sum())

    def get_column_profile(self) -> pd.DataFrame:
        """Return a richer per-column table for the column structure view.

        Columns: column name, simple type (Numeric / Text / Date / Boolean),
        pandas dtype, memory in bytes, readable memory, and % missing.
        """
        columns = ["Column", "Type", "Pandas dtype", "Memory (bytes)", "Memory", "Missing %"]
        if self.df is None:
            return pd.DataFrame(columns=columns)

        rows = []
        n_rows = max(len(self.df), 1)
        memory = self.df.memory_usage(index=False, deep=False)
        for name in self.df.columns:
            series = self.df[name]
            rows.append(
                {
                    "Column": str(name),
                    "Type": simple_type(series),
                    "Pandas dtype": str(series.dtype),
                    "Memory (bytes)": int(memory[name]),
                    "Memory": format_bytes(int(memory[name])),
                    "Missing %": f"{series.isna().sum() / n_rows:.1%}",
                }
            )
        return pd.DataFrame(rows, columns=columns)

    def get_type_counts(self) -> dict:
        """Count how many columns fall into each simple type."""
        profile = self.get_column_profile()
        return profile["Type"].value_counts().to_dict()

    # ------------------------------------------------------------------ #
    # Row exploration
    # ------------------------------------------------------------------ #
    def get_head(self, n: int = 5) -> pd.DataFrame:
        """First ``n`` rows."""
        return pd.DataFrame() if self.df is None else self.df.head(n)

    def get_tail(self, n: int = 5) -> pd.DataFrame:
        """Last ``n`` rows."""
        return pd.DataFrame() if self.df is None else self.df.tail(n)

    def get_sample(self, n: int = 5, random_state: Optional[int] = None) -> pd.DataFrame:
        """Random sample of ``n`` rows (capped at the dataset size)."""
        if self.df is None:
            return pd.DataFrame()
        return self.df.sample(n=min(n, len(self.df)), random_state=random_state)

    def get_rows(self, n: int, method: str, random_state: Optional[int] = None) -> pd.DataFrame:
        """Return ``n`` rows using one of ``EXPLORATION_METHODS``.

        Raises:
            ValueError: If ``method`` is not a known exploration method.
        """
        if method == "Head":
            return self.get_head(n)
        if method == "Tail":
            return self.get_tail(n)
        if method == "Sample":
            return self.get_sample(n, random_state)
        raise ValueError(f"Unknown exploration method: {method!r}")


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #
def simple_type(series: pd.Series) -> str:
    """Classify a column as "Boolean", "Numeric", "Date" or "Text".

    CSV files store dates as text, so a text column is labelled "Date" when
    most of its non-empty values parse as dates.
    """
    if ptypes.is_bool_dtype(series):
        return "Boolean"
    if ptypes.is_numeric_dtype(series):
        return "Numeric"
    if ptypes.is_datetime64_any_dtype(series):
        return "Date"

    values = series.dropna().astype(str).str.strip()
    values = values[values != ""].head(_DATE_SAMPLE_SIZE)
    if values.empty:
        return "Text"
    # Values that are only digits (e.g. "2024", "12") are treated as text,
    # not dates, to avoid false positives on codes and IDs.
    if values.str.fullmatch(r"\d+").all():
        return "Text"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # pandas warns when it guesses formats
        parsed = pd.to_datetime(values, errors="coerce")
    return "Date" if parsed.notna().mean() >= _DATE_PARSE_THRESHOLD else "Text"


def format_bytes(n_bytes: int) -> str:
    """Turn a byte count into a short readable string, e.g. "6.3 KB"."""
    size = float(n_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"  # unreachable, keeps type checkers happy
