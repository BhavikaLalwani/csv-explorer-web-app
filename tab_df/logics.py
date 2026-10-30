# DataFrame tab - all the calculations.
# No Streamlit code in here, only pandas, so every function can be tested
# on its own (see tests/test_tab_df_logics.py).

import warnings
from typing import IO, Optional, Union

import pandas as pd
from pandas.api import types as ptypes

# A text column counts as "Date" if at least 90% of its values look like dates.
_DATE_PARSE_THRESHOLD = 0.9
# We only check the first 200 values so big files stay fast.
_DATE_SAMPLE_SIZE = 200

# The three options in the "Exploration method" radio button.
EXPLORATION_METHODS = ("Head", "Tail", "Sample")

# If a file isn't UTF-8 (e.g. saved from Excel), we try Latin-1 next.
_ENCODINGS = ("utf-8", "latin-1")


# Holds the uploaded data and answers every question the DataFrame tab asks.
class Dataset:
    def __init__(self, file: Optional[Union[str, IO]] = None, name: str = "") -> None:
        self.name = name
        self.df: Optional[pd.DataFrame] = None
        if file is not None:
            self.set_data(file)

    # Reads a CSV file. Gives a clear error message instead of crashing
    # if the file is empty, broken, or in an unusual encoding.
    def set_data(self, file: Union[str, IO]) -> None:
        last_error: Optional[Exception] = None
        for encoding in _ENCODINGS:
            if hasattr(file, "seek"):
                file.seek(0)  # go back to the start of the file before each try
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

    # Used by streamlit_app.py, which has already read the CSV into a DataFrame.
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, name: str = "") -> "Dataset":
        dataset = cls(name=name)
        dataset.df = df
        return dataset

    def is_df_none(self) -> bool:
        return self.df is None or self.df.empty

    # ---- Numbers for the "Dataset at a glance" table ----

    def get_n_rows(self) -> int:
        return 0 if self.df is None else int(self.df.shape[0])

    def get_n_cols(self) -> int:
        return 0 if self.df is None else int(self.df.shape[1])

    # A duplicate is a row that is exactly the same as an earlier row.
    def get_n_duplicates(self) -> int:
        return 0 if self.df is None else int(self.df.duplicated().sum())

    # Counts rows that have at least one empty cell.
    def get_n_missing(self) -> int:
        return 0 if self.df is None else int(self.df.isna().any(axis=1).sum())

    def get_summary_df(self) -> pd.DataFrame:
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

    # ---- Information about each column ----

    # Column name, pandas data type and memory, in the same format as the
    # brief's screenshot (including the "Index" row at the bottom).
    def get_cols_dtype(self) -> pd.DataFrame:
        if self.df is None:
            return pd.DataFrame(columns=["column", "data_type", "memory"])

        memory = self.df.memory_usage(index=True, deep=False)
        dtypes = self.df.dtypes.reindex(memory.index)
        table = pd.DataFrame(
            {
                "column": memory.index.astype(str),
                "data_type": dtypes.astype(str).values,
                "memory": memory.values,
            }
        )
        is_index = table["column"] == "Index"
        return pd.concat([table[~is_index], table[is_index]], ignore_index=True)

    def get_total_memory(self) -> int:
        return 0 if self.df is None else int(self.df.memory_usage(index=True).sum())

    # The table shown in "Column structure": a simple type (Numeric / Text /
    # Date / Boolean), the pandas type, memory, and how much of it is missing.
    def get_column_profile(self) -> pd.DataFrame:
        columns = ["Column", "Type", "Pandas dtype", "Memory (bytes)", "Memory", "Missing %"]
        if self.df is None:
            return pd.DataFrame(columns=columns)

        rows = []
        n_rows = max(len(self.df), 1)  # avoid dividing by zero
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

    # e.g. {"Text": 2, "Numeric": 1, "Date": 1} - used for the type pills.
    def get_type_counts(self) -> dict:
        profile = self.get_column_profile()
        return profile["Type"].value_counts().to_dict()

    # ---- Rows for the "Explore rows" section ----

    def get_head(self, n: int = 5) -> pd.DataFrame:
        return pd.DataFrame() if self.df is None else self.df.head(n)

    def get_tail(self, n: int = 5) -> pd.DataFrame:
        return pd.DataFrame() if self.df is None else self.df.tail(n)

    # Never asks for more rows than the file has (that would crash).
    def get_sample(self, n: int = 5, random_state: Optional[int] = None) -> pd.DataFrame:
        if self.df is None:
            return pd.DataFrame()
        return self.df.sample(n=min(n, len(self.df)), random_state=random_state)

    # Picks head, tail or sample depending on the radio button choice.
    def get_rows(self, n: int, method: str, random_state: Optional[int] = None) -> pd.DataFrame:
        if method == "Head":
            return self.get_head(n)
        if method == "Tail":
            return self.get_tail(n)
        if method == "Sample":
            return self.get_sample(n, random_state)
        raise ValueError(f"Unknown exploration method: {method!r}")


# Works out what kind of data a column holds.
# CSV files store dates as plain text, so we test whether the text looks like dates.
def simple_type(series: pd.Series) -> str:
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
    # Only-digit values like "2024" or "12" are usually codes or IDs, not dates.
    if values.str.fullmatch(r"\d+").all():
        return "Text"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # hide pandas' "guessing the date format" warning
        parsed = pd.to_datetime(values, errors="coerce")
    return "Date" if parsed.notna().mean() >= _DATE_PARSE_THRESHOLD else "Text"


# Turns a number of bytes into something readable, e.g. 6450 -> "6.3 KB".
def format_bytes(n_bytes: int) -> str:
    size = float(n_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"
