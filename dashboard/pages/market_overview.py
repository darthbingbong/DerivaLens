from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data.validation import validate_futures_data


def _scan_market_files() -> tuple[List[Path], List[Path]]:
    """Return real parquet files under processed and synthetic directories."""
    project_root = Path(__file__).resolve().parents[2]
    processed_dir = project_root / "data" / "processed"
    synthetic_dir = project_root / "data" / "synthetic"

    processed_files = sorted((processed_dir / "futures").glob("*.parquet")) if (processed_dir / "futures").exists() else []
    synthetic_files = sorted(synthetic_dir.glob("**/*.parquet")) if synthetic_dir.exists() else []
    return processed_files, synthetic_files


def _instrument_from_filename(path: Path) -> str:
    name = path.stem
    for suffix in ["_futures", "_options", "_spot", "_synthetic"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.upper()


def _load_futures_dataframe(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if not isinstance(df.index, pd.DatetimeIndex):
        if "datetime" in df.columns:
            df = df.copy()
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df = df.dropna(subset=["datetime"]).set_index("datetime")
        elif "Date" in df.columns:
            df = df.copy()
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"]).set_index("Date")
    return df


def _get_instrument_list() -> List[str]:
    processed_files, synthetic_files = _scan_market_files()
    instruments: List[str] = []
    seen = set()
    for candidate in processed_files + synthetic_files:
        instrument = _instrument_from_filename(candidate)
        if instrument and instrument not in seen:
            seen.add(instrument)
            instruments.append(instrument)
    return sorted(instruments)


def _get_file_for_instrument(instrument: str) -> Tuple[Path | None, str]:
    processed_files, synthetic_files = _scan_market_files()
    instrument_lower = instrument.lower()

    for candidate in processed_files:
        if instrument_lower in candidate.stem.lower():
            return candidate, "LOCAL PARQUET"

    for candidate in synthetic_files:
        if instrument_lower in candidate.stem.lower():
            return candidate, "SYNTHETIC TEST DATA"

    return None, "NOT FOUND"


def _expected_schema() -> str:
    return """Expected futures schema:
- Date / datetime index
- open
- high
- low
- close
- volume
- open_interest
Optional fields may include instrument or expiry metadata."""


def render() -> None:
    st.title("Market Overview")
    st.caption("Phase 2 research interface — actual loaded market data only.")

    instruments = _get_instrument_list()

    if not instruments:
        st.warning("Historical market data not configured.")
        st.info("No parquet files were found under the project data directories.")

        project_root = Path(__file__).resolve().parents[2]
        data_dir = project_root / "data"
        processed_dir = data_dir / "processed"
        raw_dir = data_dir / "raw"

        files_detected = sum(len(list((processed_dir / kind).glob("*.parquet"))) for kind in ["futures", "options", "spot"])

        st.subheader("Data status")
        st.write(f"- Data directory: {data_dir}")
        st.write(f"- Expected schema: { _expected_schema() }")
        st.write(f"- Number of files detected: {files_detected}")
        st.write(f"- Validation status: Not available — no market data loaded.")

        with st.expander("Expected market schema", expanded=True):
            st.code(_expected_schema(), language="text")

        with st.expander("Storage locations", expanded=False):
            st.code(f"Processed data: {processed_dir}\nRaw data: {raw_dir}\nSynthetic test data: {project_root / 'data' / 'synthetic'}")
        return

    selected_instrument = st.selectbox("Instrument", instruments, index=0)
    file_path, source_label = _get_file_for_instrument(selected_instrument)

    if file_path is None:
        st.warning("No data file found for the selected instrument.")
        return

    df = _load_futures_dataframe(file_path)
    if df.empty:
        st.warning("The selected data file is empty.")
        return

    if source_label == "SYNTHETIC TEST DATA":
        st.info("SYNTHETIC TEST DATA")

    st.subheader("Data status")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data source", source_label)
    with col2:
        start_date = df.index.min() if isinstance(df.index, pd.DatetimeIndex) else pd.to_datetime(df.iloc[0].name)
        end_date = df.index.max() if isinstance(df.index, pd.DatetimeIndex) else pd.to_datetime(df.iloc[-1].name)
        st.metric("Date range", f"{start_date.date()} → {end_date.date()}")
    with col3:
        st.metric("Observations", f"{len(df):,}")
    with col4:
        inst_count = df["instrument"].nunique() if "instrument" in df.columns else 1
        st.metric("Instruments", f"{inst_count}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Missing values", int(df.isna().sum().sum()))
    with col2:
        st.metric("Duplicate rows", int(df.duplicated().sum()))
    with col3:
        invalid_price_count = 0
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                invalid_price_count += int((pd.to_numeric(df[col], errors="coerce") <= 0).sum())
        st.metric("Invalid prices", int(invalid_price_count))
    with col4:
        validation_report = validate_futures_data(df)
        st.metric("Validation", "PASS" if validation_report.passed_all_checks else "FAIL")

    st.subheader("Market data table")
    display_columns = [
        col for col in ["open", "high", "low", "close", "volume", "open_interest", "instrument"]
        if col in df.columns
    ]
    if not display_columns:
        display_columns = list(df.columns)
    st.dataframe(df[display_columns].head(100), use_container_width=True)

    if "close" in df.columns:
        st.subheader("Close price")
        close_chart_df = df[["close"]].reset_index()
        close_chart_df.columns = ["Date", "Close"]
        fig = px.line(close_chart_df, x="Date", y="Close", title=f"{selected_instrument} Close Price", hover_data={"Date": True, "Close": True})
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    if "volume" in df.columns:
        st.subheader("Volume")
        volume_df = df[["volume"]].reset_index()
        volume_df.columns = ["Date", "Volume"]
        fig = px.line(volume_df, x="Date", y="Volume", title=f"{selected_instrument} Volume", hover_data={"Date": True, "Volume": True})
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    if "open_interest" in df.columns:
        st.subheader("Open interest")
        oi_df = df[["open_interest"]].reset_index()
        oi_df.columns = ["Date", "Open Interest"]
        fig = px.line(oi_df, x="Date", y="Open Interest", title=f"{selected_instrument} Open Interest", hover_data={"Date": True, "Open Interest": True})
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data quality panel")
    quality_cols = st.columns(3)
    with quality_cols[0]:
        st.metric("Records", f"{len(df):,}")
    with quality_cols[1]:
        st.metric("Missing values", int(df.isna().sum().sum()))
    with quality_cols[2]:
        st.metric("Duplicates", int(df.duplicated().sum()))

    quality_cols = st.columns(3)
    with quality_cols[0]:
        st.metric("Invalid prices", int(invalid_price_count))
    with quality_cols[1]:
        date_coverage = "Complete" if isinstance(df.index, pd.DatetimeIndex) and not df.index.empty else "N/A"
        st.metric("Date coverage", date_coverage)
    with quality_cols[2]:
        st.metric("Validation", "PASS" if validation_report.passed_all_checks else "FAIL")


if __name__ == "__main__":
    render()
