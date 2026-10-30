"""Streamlit rendering for the DataFrame tab.

All calculations live in ``tab_df/logics.py``; this module only draws them.
The tab is laid out as a banner followed by three numbered cards:

01. Dataset at a glance  - summary table + data health checks
02. Column structure     - per-column type, dtype, memory and missing %
03. Explore rows         - slider + Head/Tail/Sample selector + rows table

Styling: every element of this tab sits inside a container with the key
``tabdf``. Streamlit gives that container the CSS class ``st-key-tabdf``, and
all the CSS below is prefixed with it, so the custom look only applies to
this tab and never leaks into the other tabs.
"""

import html

import pandas as pd
import streamlit as st

from tab_df.logics import EXPLORATION_METHODS, Dataset, format_bytes

_SLIDER_MIN = 5
_SLIDER_MAX = 50

# Icons shown next to each simple column type.
_TYPE_ICONS = {"Numeric": "🔢", "Text": "🔤", "Date": "📅", "Boolean": "✅"}

# ---------------------------------------------------------------------- #
# Theme
# ---------------------------------------------------------------------- #
# Change these to restyle the whole tab.
ACCENT = "#FF7A59"        # coral: headings, numbers, highlights
ACCENT_2 = "#3EC7B6"      # teal: "all good" states, secondary highlights
WARNING = "#F5B942"       # amber: data quality warnings
HEADING_FONT = "Space Grotesk"
BODY_FONT = "Inter"
MONO_FONT = "JetBrains Mono"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ---- Base font for everything in this tab ---- */
.st-key-tabdf, .st-key-tabdf p, .st-key-tabdf label, .st-key-tabdf td, .st-key-tabdf th {{
    font-family: '{BODY_FONT}', sans-serif;
}}

/* ---- Banner ---- */
.st-key-tabdf .tdf-hero {{
    background: linear-gradient(120deg, #1B1F3B 0%, #2B1F3F 55%, #4A2333 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 8px;
    color: #F4F1EE;
}}
.st-key-tabdf .tdf-eyebrow {{
    font-family: '{MONO_FONT}', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {ACCENT};
    margin: 0 0 6px 0;
}}
.st-key-tabdf .tdf-title {{
    font-family: '{HEADING_FONT}', sans-serif;
    font-weight: 700;
    font-size: 2.1rem;
    line-height: 1.15;
    margin: 0 0 18px 0;
    color: #FFFFFF;
    word-break: break-word;
}}
.st-key-tabdf .tdf-chips {{ display: flex; flex-wrap: wrap; gap: 10px; }}
.st-key-tabdf .tdf-chip {{
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 0.85rem;
    color: #D9D4CF;
}}
.st-key-tabdf .tdf-chip b {{
    font-family: '{MONO_FONT}', monospace;
    color: #FFFFFF;
    margin-right: 4px;
}}

/* ---- Cards ---- */
.st-key-tabdf [class*="st-key-tdfcard"] {{
    border-radius: 16px;
    border-color: rgba(128,128,128,0.25);
    background: rgba(128,128,128,0.04);
}}

/* ---- Section headers ---- */
.st-key-tabdf .tdf-section {{ display: flex; align-items: baseline; gap: 14px; margin: 4px 0 2px 0; }}
.st-key-tabdf .tdf-num {{
    font-family: '{MONO_FONT}', monospace;
    font-weight: 600;
    color: {ACCENT};
    font-size: 0.95rem;
}}
.st-key-tabdf .tdf-h {{
    font-family: '{HEADING_FONT}', sans-serif;
    font-weight: 700;
    font-size: 1.35rem;
    margin: 0;
}}
.st-key-tabdf .tdf-sub {{ opacity: 0.6; font-size: 0.88rem; margin: 0 0 12px 0; }}
.st-key-tabdf .tdf-label {{
    font-family: '{MONO_FONT}', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    opacity: 0.6;
    margin: 6px 0 8px 0;
}}

/* ---- Static tables ---- */
.st-key-tabdf [data-testid="stTable"] thead th {{
    font-family: '{MONO_FONT}', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {ACCENT};
}}
/* Row labels (column names, descriptions): keep their real spelling. */
.st-key-tabdf [data-testid="stTable"] tbody th {{
    font-weight: 600;
    font-size: 0.9rem;
}}
.st-key-tabdf [data-testid="stTable"] td {{ font-size: 0.9rem; }}

/* ---- Health badges ---- */
.st-key-tabdf .tdf-badge {{
    display: flex; align-items: center; gap: 10px;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.9rem;
}}
.st-key-tabdf .tdf-badge.ok   {{ background: {ACCENT_2}1F; border: 1px solid {ACCENT_2}66; }}
.st-key-tabdf .tdf-badge.warn {{ background: {WARNING}1F; border: 1px solid {WARNING}66; }}
.st-key-tabdf .tdf-dot {{ width: 9px; height: 9px; border-radius: 50%; flex: none; }}
.st-key-tabdf .ok .tdf-dot   {{ background: {ACCENT_2}; }}
.st-key-tabdf .warn .tdf-dot {{ background: {WARNING}; }}
.st-key-tabdf .tdf-badge b {{ font-family: '{MONO_FONT}', monospace; }}

/* ---- Column type pills ---- */
.st-key-tabdf .tdf-pills {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.st-key-tabdf .tdf-pill {{
    border: 1px solid rgba(128,128,128,0.35);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.85rem;
}}
.st-key-tabdf .tdf-pill b {{ font-family: '{MONO_FONT}', monospace; color: {ACCENT}; }}

/* ---- Widgets ---- */
.st-key-tabdf [data-testid="stWidgetLabel"] p {{ font-weight: 600; }}
.st-key-tabdf .tdf-rows-info {{
    font-family: '{MONO_FONT}', monospace;
    font-size: 0.8rem;
    color: {ACCENT_2};
    margin: 4px 0 8px 0;
}}
</style>
"""


# ---------------------------------------------------------------------- #
# Entry points
# ---------------------------------------------------------------------- #
def display_df_tab(df: pd.DataFrame, file_name: str = "") -> None:
    """Render the DataFrame tab from a DataFrame loaded by streamlit_app.py.

    Matches the team convention (``display_numeric_tab(df)`` etc.).

    Args:
        df: The uploaded CSV as a DataFrame.
        file_name: Optional file name shown in the banner.
    """
    if df is None:
        st.warning("No data loaded.")
        return
    display_tab_df_content(Dataset.from_dataframe(df, name=file_name))


def display_tab_df_content(dataset: Dataset) -> None:
    """Render the whole DataFrame tab for an already loaded ``Dataset``."""
    if dataset.is_df_none():
        st.warning("The uploaded file contains no data to display.")
        return

    st.markdown(_CSS, unsafe_allow_html=True)
    with st.container(key="tabdf"):
        _display_hero(dataset)
        display_overall_df(dataset)
        display_columns_df(dataset)
        display_explore_df(dataset)


# ---------------------------------------------------------------------- #
# Sections
# ---------------------------------------------------------------------- #
def _display_hero(dataset: Dataset) -> None:
    """Banner with the file name and headline numbers."""
    name = html.escape(dataset.name or "Uploaded dataset")  # never trust file names
    chips = [
        (f"{dataset.get_n_rows():,}", "rows"),
        (f"{dataset.get_n_cols():,}", "columns"),
        (format_bytes(dataset.get_total_memory()), "in memory"),
    ]
    chips_html = "".join(f'<span class="tdf-chip"><b>{value}</b>{label}</span>' for value, label in chips)
    st.markdown(
        f"""
        <div class="tdf-hero">
            <p class="tdf-eyebrow">Dataset overview</p>
            <p class="tdf-title">{name}</p>
            <div class="tdf-chips">{chips_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_overall_df(dataset: Dataset) -> None:
    """Card 01: static summary table next to automatic data health checks."""
    with st.container(border=True, key="tdfcard_overall"):
        _section_header("01", "Dataset at a glance", "Size and quality of the whole file.")
        left, right = st.columns([3, 2], gap="large")

        with left:
            st.table(dataset.get_summary_df().set_index("Description"))

        with right:
            st.markdown('<p class="tdf-label">Data health</p>', unsafe_allow_html=True)
            n_rows = dataset.get_n_rows()
            badges = _health_badge(dataset.get_n_duplicates(), n_rows, "duplicated row", "duplicated rows")
            badges += _health_badge(
                dataset.get_n_missing(), n_rows, "row with missing values", "rows with missing values"
            )
            st.markdown(badges, unsafe_allow_html=True)

            st.markdown('<p class="tdf-label">Column types</p>', unsafe_allow_html=True)
            pills = "".join(
                f'<span class="tdf-pill">{_TYPE_ICONS.get(kind, "•")} {kind} <b>{count}</b></span>'
                for kind, count in dataset.get_type_counts().items()
            )
            st.markdown(f'<div class="tdf-pills">{pills}</div>', unsafe_allow_html=True)


def display_columns_df(dataset: Dataset) -> None:
    """Card 02: static table of every column's type, memory and missing share."""
    with st.container(border=True, key="tdfcard_columns"):
        _section_header(
            "02",
            "Column structure",
            "Type, memory use and missing values for every column.",
        )
        profile = dataset.get_column_profile()
        profile["Type"] = profile["Type"].map(lambda kind: f"{_TYPE_ICONS.get(kind, '•')} {kind}")
        st.table(profile.set_index("Column"))
        st.caption(
            "Memory is shallow pandas memory usage per column. "
            "A text column is labelled Date when 90% of its values parse as dates."
        )


def display_explore_df(dataset: Dataset) -> None:
    """Card 03: choose how many rows and which rows to look at."""
    with st.container(border=True, key="tdfcard_explore"):
        _section_header("03", "Explore rows", "Browse the first, last or a random set of rows.")
        n_total = dataset.get_n_rows()
        max_rows = min(_SLIDER_MAX, n_total)
        min_rows = min(_SLIDER_MIN, max_rows)

        controls_left, controls_right = st.columns([3, 2], gap="large")
        with controls_left:
            if max_rows > min_rows:
                n_rows = st.slider(
                    "Number of rows to display",
                    min_value=min_rows,
                    max_value=max_rows,
                    value=min_rows,
                    key="tab_df_n_rows",
                )
            else:
                # Too few rows for a slider range; show them all.
                n_rows = max_rows
                st.caption(f"The dataset only has {max_rows} row(s), so all are shown.")
        with controls_right:
            method = st.radio(
                "Exploration method",
                EXPLORATION_METHODS,
                horizontal=True,
                key="tab_df_method",
            )
            if method == "Sample":
                st.button("🔀 Draw a new sample", key="tab_df_resample")

        st.markdown(
            f'<p class="tdf-rows-info">▸ {_rows_caption(method, n_rows, n_total)}</p>',
            unsafe_allow_html=True,
        )
        st.dataframe(dataset.get_rows(n_rows, method))


# ---------------------------------------------------------------------- #
# Small HTML helpers
# ---------------------------------------------------------------------- #
def _section_header(number: str, title: str, subtitle: str) -> None:
    """Numbered card heading, e.g. "01  Dataset at a glance"."""
    st.markdown(
        f"""
        <div class="tdf-section"><span class="tdf-num">{number}</span>
        <p class="tdf-h">{title}</p></div>
        <p class="tdf-sub">{subtitle}</p>
        """,
        unsafe_allow_html=True,
    )


def _health_badge(count: int, total: int, singular: str, plural: str) -> str:
    """HTML badge: teal when ``count`` is zero, amber with a % otherwise."""
    if count == 0:
        return f'<div class="tdf-badge ok"><span class="tdf-dot"></span>No {plural}</div>'
    label = singular if count == 1 else plural
    return (
        f'<div class="tdf-badge warn"><span class="tdf-dot"></span>'
        f"<span><b>{count:,}</b> {label} ({count / total:.1%})</span></div>"
    )


def _rows_caption(method: str, n_rows: int, n_total: int) -> str:
    """Describe which rows are currently shown, e.g. "rows 1–5 of 801"."""
    if method == "Head":
        return f"First {n_rows} rows · rows 1–{n_rows} of {n_total:,}"
    if method == "Tail":
        return f"Last {n_rows} rows · rows {n_total - n_rows + 1:,}–{n_total:,} of {n_total:,}"
    return f"{n_rows} random rows out of {n_total:,} · press the button for a new sample"
