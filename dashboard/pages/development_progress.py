from __future__ import annotations

import streamlit as st


def render_progress() -> None:
    st.title("Development Progress")
    st.caption("Project implementation status and roadmap tracking for engineers and contributors.")

    stage_rows = [
        ("Phase 1", "Architecture & configuration", "Complete"),
        ("Phase 2", "Market data pipeline", "Complete"),
        ("Phase 3", "Futures analytics", "Planned"),
        ("Phase 4", "Options analytics", "Planned"),
        ("Phase 5", "Volatility analytics", "Planned"),
        ("Phase 6", "Market regime detection", "Planned"),
        ("Phase 7", "Strategy lab", "Planned"),
        ("Phase 8", "Backtesting engine", "Planned"),
        ("Phase 9", "Risk analytics", "Planned"),
        ("Phase 10", "Walk-forward validation", "Planned"),
        ("Phase 11", "Statistics & benchmarking", "Planned"),
        ("Phase 12", "Dashboard enhancement", "Planned"),
        ("Phase 13", "Research reporting", "Planned"),
        ("Phase 14", "Final polish", "Planned"),
    ]

    st.table({"Phase": [r[0] for r in stage_rows], "Scope": [r[1] for r in stage_rows], "Status": [r[2] for r in stage_rows]})

    st.subheader("Validation status")
    st.write("- Phase 1 validation: implemented and passing")
    st.write("- Phase 2 validation: implemented and passing")
    st.write("- Current product UI: market-data only")

    st.subheader("Architecture")
    st.code(
        "dashboard/app.py\n  → navigation shell\n  → page dispatch\n\nsrc/data/\n  → ingestion / validation / cleaning / storage\nsrc/futures/\nsrc/options/\nsrc/volatility/\nsrc/regimes/\nsrc/strategies/\nsrc/backtesting/\nsrc/risk/\n",
        language="text",
    )
