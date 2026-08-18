from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


def _count_parquet_files(directory: Path) -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob("**/*.parquet")))


def render_data_status() -> None:
    st.title("Data Status")
    st.caption("Current available market-data state for the project.")

    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    synthetic_dir = data_dir / "synthetic"

    source_info = {
        "Data directory": str(data_dir),
        "Raw data": str(raw_dir),
        "Processed data": str(processed_dir),
        "Synthetic test data": str(synthetic_dir),
    }

    for label, value in source_info.items():
        st.write(f"- {label}: {value}")

    st.subheader("File inventory")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Raw files", _count_parquet_files(raw_dir))
    with col2:
        st.metric("Processed files", _count_parquet_files(processed_dir))
    with col3:
        st.metric("Synthetic files", _count_parquet_files(synthetic_dir))

    st.subheader("Active status")
    if _count_parquet_files(processed_dir) == 0 and _count_parquet_files(synthetic_dir) == 0:
        st.warning("Historical market data not configured.")
        st.write("No market data is currently available in the project data directories.")
    else:
        st.success("Data files detected.")

    with st.expander("Expected futures schema", expanded=True):
        st.code(
            "Date / datetime index\nopen\nhigh\nlow\nclose\nvolume\nopen_interest",
            language="text",
        )
