# CSV Explorer Web Application

An interactive **Streamlit** application for exploring uploaded CSV datasets, inspecting data quality, and analysing numerical and text columns without writing code.

## Features

### 1. DataFrame overview

The **DataFrame** tab provides a high-level view of the uploaded dataset:

- Total row and column counts and estimated memory usage.
- Data-quality indicators, including duplicate rows and rows with missing values.
- Column names, data types, memory usage, and missing-value proportions.
- Row inspection using **head**, **tail**, or **sample** selection.

### 2. Numeric Serie

Select a numeric column to view:

- Unique values, missing values, zeros, and negative values.
- Mean, standard deviation, minimum, maximum, and median.
- A binned histogram showing the distribution of values.
- The 20 most frequent numeric values, with occurrence counts and proportions.

Only numeric columns are offered in the selector. Missing values are omitted from the histogram and frequency list.

### 3. Text Serie

Select a text column and click **Analyze Text Column** to view:

- Number of distinct non-missing values.
- Missing-value and blank/whitespace-only string counts.
- Average, minimum, and maximum text lengths, measured in **characters**.
- The 20 most frequent text values, with counts and proportions.
- An interactive Altair horizontal bar chart of frequent values.

The selector includes Pandas `object` and `string` columns. The frequency percentages use **all rows** as the denominator, including rows with missing values, so the percentages shown for non-missing values need not total 100%.

## Technology stack

- **Python** — application and analysis logic.
- **Streamlit** — interactive web interface.
- **Pandas** — CSV ingestion, data types, summary statistics, and frequency calculations.
- **Altair** — histograms and categorical frequency charts.
- **Pytest** — automated testing (development dependency).
- **Git and GitHub** — version control and collaboration.

## Getting started

### Prerequisites

- Python 3 and `pip` installed.
- Git (if cloning the repository).
- A CSV file to explore.

### 1. Clone the repository

```bash
git clone https://github.com/BhavikaLalwani/csv-explorer-web-app.git
cd csv-explorer-web-app
```

### 2. Create and activate a virtual environment (recommended)

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

The repository's `requirements.txt` lists `streamlit`, `pandas`, and `altair`.

### 4. Start the application

From the **repository root**, run:

```bash
python -m streamlit run app/streamlit_app.py
```

Streamlit normally opens the app in your browser. If it does not, visit the local address printed in the terminal (typically `http://localhost:8501`). Leave the terminal running while using the app; press **Ctrl+C** to stop it.

> **Troubleshooting:** If `streamlit` is reported as an unknown command, use `python -m streamlit` as above. If Python reports `No module named streamlit`, activate the correct environment and reinstall the requirements.

## How to use

1. Start the application and choose a `.csv` file using the upload control.
2. Open **DataFrame** to inspect dataset size, quality, columns, and sample rows.
3. Open **Numeric Serie**, select a numeric column, and review its statistics and histogram.
4. Open Text Serie, select a text column, and click Analyze Text Column to display summary statistics, frequent values, and a frequency distribution chart.
5. Open **Datetime Serie** to view its current placeholder until that module is implemented.

**Example:** For a dataset containing `Borough` (text) and `Population` (number), select `Borough` in Text Serie to examine category frequencies and `Population` in Numeric Serie to examine numerical distributions.

## Project structure

```text
csv-explorer-web-app/
├── app/
│   └── streamlit_app.py       # CSV upload and main tab navigation
├── tab_df/
│   ├── display.py             # Dataset overview and row-exploration UI
│   └── logics.py              # DataFrame summary and profiling helpers
├── tab_numeric/
│   ├── display.py             # Numeric statistics and histogram UI
│   └── logics.py              # Numeric calculations
├── tab_text/
│   ├── display.py             # Text selection, tables and chart UI
│   └── logics.py              # Text statistics and frequency calculations
├── tab_date/
│   ├── display.py             # Reserved for datetime UI
│   └── logics.py              # Reserved for datetime logic
├── tests/
│   ├── test_tab_df_logics.py
│   └── test_tab_text_logics.py  # Text analysis unit tests
├── requirements.txt
├── .gitignore
└── README.md
```

The project separates **display** functions from **logic** functions so that calculations can be tested independently of the interface.

## Testing

Install Pytest if necessary:

```bash
python -m pip install pytest
```

Run the full test suite from the repository root:

```bash
python -m pytest tests/ -v
```

To run only the text module tests (when present):

```bash
python -m pytest tests/test_tab_text_logics.py -v
```

The text module includes four tests covering column detection, summary statistics, frequent values, and all-missing input. During local testing, all 39 automated tests passed successfully, including four tests specifically designed for the Text Serie module. This is a recorded local result, not a guarantee for later revisions or other environments.

## Known limitations

- The application reads CSV files through Pandas; unusual encodings, malformed CSVs, or very large datasets may require preprocessing or additional memory.
- Column selection is based on inferred Pandas data types. A numeric-looking field stored as text may appear in the text selector.
- Text statistics operate on complete cell values, not sentiment, language, or individual-word frequencies.
- Blank strings and missing/null values are counted separately; blank cells may be interpreted as missing by `pandas.read_csv` under its default settings.
- Datetime analysis remains a placeholder in the reviewed snapshot.

## Potential improvements

- Implement datetime-column detection, parsing, and date-range analysis.
- Add optional filters and downloadable analysis summaries.
- Support configurable frequency limits and richer categorical charts.
- Improve handling of large files, file encodings, and CSV parsing errors.
- Add more automated edge-case tests and continuous integration checks.

## Collaboration and contributions

Development is organised into separate modules and Git feature branches. For new changes:

1. Create a branch from the latest project baseline.
2. Implement and test the change locally.
3. Commit only relevant files.
4. Push the branch and open a pull request against `main`.
5. Request review before merging.

## Repository

[BhavikaLalwani/csv-explorer-web-app](https://github.com/BhavikaLalwani/csv-explorer-web-app)

## License

No project license was identified in the reviewed uploaded snapshot. Do not assume that the repository is licensed for unrestricted redistribution; the maintainers should add a `LICENSE` file if they wish to specify reuse terms.
