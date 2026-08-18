"""
Phase 1: Project Architecture Page

Displays project structure, configuration system, and setup status.
Business logic stays in src/config.py - this page just displays it.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from dashboard.utils.theme import create_info_box, ColorPalette
from dashboard.utils.navigation import create_phase_breadcrumb


def render():
    """Render Phase 1 architecture page."""
    
    # Header
    st.title("📋 Phase 1: Project Architecture & Configuration")
    create_phase_breadcrumb(1)
    st.markdown("---")
    
    # Phase status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "✅ Complete", delta="14 phases total")
    with col2:
        st.metric("Lines of Code", "~2,100", delta="+configuration system")
    with col3:
        st.metric("Test Coverage", "12/12", delta="100% passing")
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Configuration", "Project Structure", "Status"])
    
    # TAB 1: Overview
    with tab1:
        st.subheader("📖 Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### About DerivaLens
            
            **DerivaLens** is a regime-aware futures & options research and backtesting engine built as an educational platform for the Futures First internship.
            
            **Key Characteristics:**
            - Educational focus on quantitative research
            - Regime-aware strategy analysis
            - Professional backtesting infrastructure
            - Modular, extensible architecture
            """)
        
        with col2:
            st.markdown("""
            ### Project Goals
            
            - Demonstrate when and why strategies work in different market regimes
            - Build institutional-style research platform
            - Show proper data handling and validation
            - Implement walk-forward validation
            - Create comprehensive performance reporting
            """)
        
        st.markdown("---")
        
        st.subheader("🎯 14-Phase Development Roadmap")
        
        phases_data = [
            ("1", "Architecture", "Configuration & structure", "✅"),
            ("2", "Data Pipeline", "Ingestion & validation", "✅"),
            ("3", "Futures Processing", "Basis, rolling, spreads", "⏳"),
            ("4", "Options Processing", "Greeks, IV surface", "⏳"),
            ("5", "Volatility", "RV, IV, smile/skew", "⏳"),
            ("6", "Regime Detection", "Market regimes", "⏳"),
            ("7", "Strategies", "Trading strategies", "⏳"),
            ("8", "Backtesting", "Performance testing", "⏳"),
            ("9", "Risk Analysis", "Risk metrics", "⏳"),
            ("10", "Walk-Forward", "Out-of-sample validation", "⏳"),
            ("11", "Statistics", "Performance statistics", "⏳"),
            ("12", "Dashboard", "Interactive UI", "⏳"),
            ("13", "Reports", "Report generation", "⏳"),
            ("14", "Polish", "Documentation & finalization", "⏳"),
        ]
        
        col1, col2 = st.columns([0.3, 0.7])
        with col1:
            phase_list = "\n".join([
                f"{status} Phase {num}: {name}" 
                for num, name, _, status in phases_data
            ])
            st.code(phase_list, language="text")
        
        with col2:
            # Progress
            completed = sum(1 for _, _, _, status in phases_data if "✅" in status)
            total = len(phases_data)
            progress = completed / total
            
            st.progress(progress)
            st.caption(f"Progress: {completed}/{total} phases completed ({progress*100:.0f}%)")
            
            st.markdown(f"""
            - **Completed**: {completed} phases ✅
            - **In Development**: 1 phase ⏳
            - **Planned**: {total - completed - 1} phases
            """)
    
    # TAB 2: Configuration System
    with tab2:
        st.subheader("⚙️ Configuration System")
        
        try:
            config = get_config()
            
            create_info_box(
                "Configuration System Ready",
                "Configuration is loaded from YAML files and accessible throughout the application.",
                "success"
            )
            
            # Configuration structure
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### Configuration Files
                
                **config/config.yaml**
                - Project metadata
                - Backtesting parameters
                - Strategy configurations
                - Volatility methods
                - Risk parameters
                - Logging settings
                """)
            
            with col2:
                st.markdown("""
                ### Configuration Files (cont'd)
                
                **config/instruments.yaml**
                - Instrument specifications
                - Contract details
                - Multipliers and tick sizes
                - Exchange information
                """)
            
            st.markdown("---")
            
            # Display sample config
            st.subheader("Sample Configuration Values")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Initial Capital", "Rs 1,000,000")
                st.metric("Max Leverage", "2.0x")
                st.metric("Slippage", "2.0 bps")
            
            with col2:
                st.metric("Commission", "1.0 bps")
                st.metric("Risk per Trade", "2.0%")
                st.metric("Risk-Free Rate", "5.0%")
            
            with col3:
                st.metric("Outlier Threshold", "5.0σ")
                st.metric("Min Price", "₹0.01")
                st.metric("Max Leverage", "2.0x")
            
            # Configuration access example
            st.markdown("---")
            st.subheader("💻 Configuration Access Pattern")
            
            code_example = """python
from src.config import get_config

config = get_config()

# Dot notation access
initial_capital = config.get('backtesting.initial_capital')
slippage_bps = config.get('backtesting.slippage_bps')
nifty_config = config.get_instrument('NIFTY')

# Default values
timeout = config.get('some_key', default_value=30)
"""
            
            st.code(code_example, language="python")
            
        except Exception as e:
            st.error(f"Error loading configuration: {e}")
    
    # TAB 3: Project Structure
    with tab3:
        st.subheader("📁 Project Structure")
        
        structure = """
DerivaLens/
├── src/                          # Main source code
│   ├── config.py                 # Configuration loader (singleton)
│   ├── data/                      # Data processing
│   │   ├── ingestion.py          # Data providers (synthetic, parquet)
│   │   ├── validation.py         # Data quality checks
│   │   ├── cleaning.py           # Data cleaning pipeline
│   │   └── storage.py            # Parquet storage management
│   ├── futures/                   # Futures analysis (Phase 3+)
│   ├── options/                   # Options analysis (Phase 4+)
│   ├── volatility/                # Volatility analysis (Phase 5+)
│   ├── regimes/                   # Regime detection (Phase 6+)
│   ├── strategies/                # Trading strategies (Phase 7+)
│   ├── backtesting/               # Backtesting engine (Phase 8+)
│   ├── risk/                      # Risk analysis (Phase 9+)
│   └── reporting/                 # Report generation (Phase 13+)
├── config/                        # Configuration files
│   ├── config.yaml                # Main configuration
│   └── instruments.yaml           # Instrument definitions
├── tests/                         # Unit tests
│   ├── test_config.py            # Configuration tests (12 tests)
│   └── test_data.py              # Data module tests (29 tests)
├── dashboard/                     # Streamlit dashboard
│   ├── app.py                     # Main app entry point
│   ├── pages/                     # Page modules (1 per phase)
│   │   ├── phase1_architecture.py
│   │   ├── phase2_data_pipeline.py
│   │   └── phase3+.py
│   ├── utils/                     # UI utilities
│   │   ├── theme.py              # Styling and theme
│   │   ├── navigation.py         # Navigation management
│   │   └── logging.py            # Logging utilities
│   └── components/                # Reusable components
├── notebooks/                     # Jupyter notebooks (research)
├── data/                          # Data storage
│   ├── raw/                       # Raw input data
│   ├── processed/                 # Cleaned data
│   │   ├── futures/
│   │   ├── options/
│   │   └── spot/
│   └── features/                  # Feature engineering
├── reports/                       # Generated reports
├── README.md                      # Project overview
├── DEVELOPMENT.md                 # Development roadmap
├── PHASE1_COMPLETE.md            # Phase 1 summary
├── PHASE2_COMPLETE.md            # Phase 2 summary
└── requirements.txt               # Python dependencies
        """
        
        st.code(structure, language="text")
    
    # TAB 4: Status & Validation
    with tab4:
        st.subheader("✅ Phase 1 Validation Status")
        
        validation_items = [
            ("✅", "Project directory structure (23 files)"),
            ("✅", "Configuration system (YAML loader, singleton pattern)"),
            ("✅", "Unit test framework (12 config tests passing)"),
            ("✅", "Data provider interface skeleton"),
            ("✅", "Module stubs for all 9 core modules"),
            ("✅", "Comprehensive documentation"),
            ("✅", "Python environment (.venv with dependencies)"),
            ("✅", "Validation automation (36/36 checks passing)"),
        ]
        
        create_info_box(
            "Phase 1 Complete",
            f"All {len(validation_items)} deliverables completed and validated.",
            "success"
        )
        
        for status, item in validation_items:
            st.write(f"{status} {item}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Test Results")
            st.metric("Configuration Tests", "12/12", delta="✅ 100% passing")
            
        with col2:
            st.subheader("📈 Code Metrics")
            st.metric("Lines of Code", "~2,100", delta="+architecture & config")
    
    st.markdown("---")
    
    # Footer
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Proceed to Phase 2", use_container_width=True):
            st.session_state.current_page = "phase2_data_pipeline"
            st.rerun()
    
    with col2:
        st.caption("Next: Phase 2 - Data Pipeline")
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_page = None
            st.rerun()
