"""
DerivaLens Dashboard - Main Application

Modular Streamlit app that incrementally exposes functionality from each phase.
This shell will be updated after each phase to add new pages while preserving existing ones.

Architecture:
- dashboard/app.py (main entry point, navigation)
- dashboard/pages/ (individual phase pages)
- dashboard/utils/ (UI helpers, formatting, styling)
- dashboard/components/ (reusable Streamlit components)

Each phase adds a new page without modifying existing ones.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dashboard.utils.theme import setup_theme, apply_custom_styling
from dashboard.utils.navigation import NavigationManager
from dashboard.utils.logging import setup_streamlit_logging

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="DerivaLens - Futures & Options Research Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "# DerivaLens\nRegime-aware futures & options research and backtesting engine.\n\nBuilt as educational platform for Futures First internship.",
        "Get Help": "https://github.com/derivalens/derivalens"
    }
)

# ============================================================================
# Setup
# ============================================================================

setup_theme()
apply_custom_styling()
setup_streamlit_logging()

# ============================================================================
# Sidebar Navigation
# ============================================================================

st.sidebar.title("🎯 DerivaLens")
st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")

nav_manager = NavigationManager()

# Phase indicators with completion status
phase_sections = {
    "Foundation": {
        "Phase 1": ("📋 Architecture", "phase1_architecture", "✅"),
        "Phase 2": ("📥 Data Pipeline", "phase2_data_pipeline", "✅"),
    },
    "Analysis": {
        "Phase 3": ("📈 Futures Processing", "phase3_futures", "⏳"),
        "Phase 4": ("📊 Options Processing", "phase4_options", "⏳"),
        "Phase 5": ("📉 Volatility Analysis", "phase5_volatility", "⏳"),
        "Phase 6": ("🔄 Regime Detection", "phase6_regimes", "⏳"),
    },
    "Strategy": {
        "Phase 7": ("🎯 Strategies", "phase7_strategies", "⏳"),
        "Phase 8": ("🧪 Backtesting", "phase8_backtesting", "⏳"),
        "Phase 9": ("⚠️ Risk Analysis", "phase9_risk", "⏳"),
        "Phase 10": ("🔁 Walk-Forward", "phase10_walkforward", "⏳"),
    },
    "Reporting": {
        "Phase 11": ("📊 Statistics", "phase11_statistics", "⏳"),
        "Phase 12": ("🎨 Dashboard", "phase12_dashboard", "⏳"),
        "Phase 13": ("📄 Reports", "phase13_reports", "⏳"),
        "Phase 14": ("✨ Polish", "phase14_polish", "⏳"),
    }
}

# Build navigation sidebar
current_page = None
for section_name, phases in phase_sections.items():
    with st.sidebar.expander(section_name, expanded=(section_name == "Foundation")):
        for phase_name, (display_name, page_key, status) in phases.items():
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                if st.button(display_name, key=f"btn_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
            with col2:
                st.caption(status)

# Get current page from session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "phase1_architecture"

current_page = st.session_state.current_page

# ============================================================================
# Project Info Sidebar
# ============================================================================

st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About Project", expanded=False):
    st.markdown("""
    **DerivaLens** is a regime-aware futures & options research and backtesting engine.
    
    **Vision**: Educational platform demonstrating:
    - When and why strategies work in different market regimes
    - Robust data pipelines and quality assurance
    - Quantitative research workflows
    - Professional backtesting practices
    
    **Status**: Phase 2 Complete ✅
    - Phase 1: Architecture & Configuration
    - Phase 2: Data Validation & Cleaning
    - Phases 3-14: In development
    """)

st.sidebar.markdown("---")
with st.sidebar.expander("📚 Quick Links", expanded=False):
    st.markdown("""
    - [GitHub Repository](https://github.com/derivalens)
    - [Documentation](../README.md)
    - [Development Roadmap](../DEVELOPMENT.md)
    - [Phase 1 Summary](../PHASE1_COMPLETE.md)
    - [Phase 2 Summary](../PHASE2_COMPLETE.md)
    """)

# ============================================================================
# Page Content
# ============================================================================

# Import pages dynamically
if current_page == "phase1_architecture":
    from dashboard.pages import phase1_architecture
    phase1_architecture.render()
    
elif current_page == "phase2_data_pipeline":
    from dashboard.pages import phase2_data_pipeline
    phase2_data_pipeline.render()

else:
    # Phase not yet implemented
    st.title(f"🚀 Coming Soon")
    st.info("""
    This phase is not yet implemented. Check back after the next development cycle!
    
    **Current Progress**: Phase 2 ✅  
    **Next**: Phase 3 - Futures Data Processing
    """)
    
    # Show roadmap
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Completed Phases
        - ✅ **Phase 1**: Project architecture and configuration
        - ✅ **Phase 2**: Data ingestion, validation, and cleaning
        """)
    with col2:
        st.markdown("""
        ### Upcoming Phases
        - ⏳ **Phase 3**: Futures-specific analysis
        - ⏳ **Phase 4**: Options chain processing
        - ⏳ ... 14 phases total
        """)

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🎓 Built as educational project for Futures First internship")
with col2:
    st.caption("📊 Regime-aware research platform")
with col3:
    st.caption("v0.2 (Phase 2 Complete)")
