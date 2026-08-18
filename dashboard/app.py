"""DerivaLens dashboard entry point.

This app exposes the actual research functionality available in the project.
The UI remains modular, but it is intentionally research-focused rather than
being a project management tracker.
"""

from pathlib import Path
import sys

import streamlit as st

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dashboard.utils.theme import apply_custom_styling, setup_theme
from dashboard.utils.logging import setup_streamlit_logging

st.set_page_config(
    page_title="DerivaLens",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "DerivaLens — quantitative derivatives research and backtesting.",
        "Get Help": "https://github.com/derivalens/derivalens",
    },
)

setup_theme()
apply_custom_styling()
setup_streamlit_logging()

st.sidebar.title("DerivaLens")
st.sidebar.caption("Quantitative derivatives research and backtesting")
st.sidebar.markdown("---")

research_pages = {
    "Market Overview": "market_overview",
    "Futures Analytics": "futures_analytics",
    "Options Analytics": "options_analytics",
    "Volatility": "volatility",
    "Market Regime": "market_regime",
    "Strategy Lab": "strategy_lab",
    "Backtesting": "backtesting",
    "Risk Analysis": "risk_analysis",
    "Research Report": "research_report",
}

system_pages = {
    "Data Status": "data_status",
    "Development Progress": "development_progress",
}

if "current_page" not in st.session_state:
    st.session_state.current_page = "market_overview"

with st.sidebar.expander("Research", expanded=True):
    for label, page_key in research_pages.items():
        if st.button(label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.current_page = page_key

with st.sidebar.expander("System", expanded=False):
    for label, page_key in system_pages.items():
        if st.button(label, key=f"sys_{page_key}", use_container_width=True):
            st.session_state.current_page = page_key

st.sidebar.markdown("---")
with st.sidebar.expander("Project status", expanded=False):
    st.caption("Current product scope: Phase 2 market-data features only.")
    st.caption("Not a project roadmap view.")

current_page = st.session_state.current_page

page_map = {
    "market_overview": "dashboard.pages.market_overview",
    "data_status": "dashboard.pages.data_status",
    "development_progress": "dashboard.pages.development_progress",
    "futures_analytics": "dashboard.pages.not_implemented",
    "options_analytics": "dashboard.pages.not_implemented",
    "volatility": "dashboard.pages.not_implemented",
    "market_regime": "dashboard.pages.not_implemented",
    "strategy_lab": "dashboard.pages.not_implemented",
    "backtesting": "dashboard.pages.not_implemented",
    "risk_analysis": "dashboard.pages.not_implemented",
    "research_report": "dashboard.pages.not_implemented",
}

if current_page in page_map:
    module_name = page_map[current_page]
    module = __import__(module_name, fromlist=["render"])

    if current_page == "futures_analytics":
        module.render("Futures Analytics", "Futures analytics will be enabled after Phase 3.")
    elif current_page == "options_analytics":
        module.render("Options Analytics", "Options analytics will be enabled after Phase 4.")
    elif current_page == "volatility":
        module.render("Volatility", "Volatility analytics will be enabled after Phase 5.")
    elif current_page == "market_regime":
        module.render("Market Regime", "Regime detection will be enabled after Phase 6.")
    elif current_page == "strategy_lab":
        module.render("Strategy Lab", "Strategy research will be enabled after the strategy modules are implemented.")
    elif current_page == "backtesting":
        module.render("Backtesting", "Backtesting will be enabled after the backtesting engine is implemented.")
    elif current_page == "risk_analysis":
        module.render("Risk Analysis", "Risk analytics will be enabled after the risk engine is implemented.")
    elif current_page == "research_report":
        module.render("Research Report", "Research reporting will be enabled after the research pipeline is implemented.")
    elif current_page == "data_status":
        module.render_data_status()
    elif current_page == "development_progress":
        module.render_progress()
    else:
        module.render()
else:
    st.title("DerivaLens")
    st.info("No page selected.")

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Research interface")
with col2:
    st.caption("Phase 2: market data")
with col3:
    st.caption("Data-first workflow")
