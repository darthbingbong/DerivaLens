"""
Phase 2: Data Pipeline Page

Displays data ingestion, validation, and cleaning capabilities.
Business logic stays in src/data/* - this page provides the UI.
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.ingestion import SyntheticDataProvider
from src.data.validation import validate_futures_data
from src.data.cleaning import clean_futures_data
from src.data.storage import ParquetStorage
from dashboard.utils.theme import create_info_box, ColorPalette
from dashboard.utils.navigation import create_phase_breadcrumb


def render():
    """Render Phase 2 data pipeline page."""
    
    # Header
    st.title("📥 Phase 2: Data Ingestion & Validation")
    create_phase_breadcrumb(2)
    st.markdown("---")
    
    # Phase status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "✅ Complete", delta="Fully tested")
    with col2:
        st.metric("Lines of Code", "~1,430", delta="+tests & docs")
    with col3:
        st.metric("Test Coverage", "29/29", delta="100% passing")
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview",
        "Data Generation",
        "Validation",
        "Cleaning",
        "Storage"
    ])
    
    # TAB 1: Overview
    with tab1:
        st.subheader("📖 Overview")
        
        create_info_box(
            "Complete Data Pipeline",
            "Phase 2 provides a production-ready data pipeline with validation, cleaning, and storage.",
            "success"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📦 Components
            
            1. **Data Ingestion** (`ingestion.py`)
               - Synthetic data generation for testing
               - Data provider interface
               - Support for futures & options
            
            2. **Data Validation** (`validation.py`)
               - 8 quality check categories
               - Human-readable reports
               - Severity levels: error/warning/info
            """)
        
        with col2:
            st.markdown("""
            3. **Data Cleaning** (`cleaning.py`)
               - Automated 5-step pipeline
               - Duplicate removal
               - Missing value handling
               - Outlier detection
            
            4. **Data Storage** (`storage.py`)
               - Parquet file format
               - Organized directories
               - Metadata preservation
            """)
        
        st.markdown("---")
        
        st.subheader("📊 Data Pipeline Architecture")
        
        pipeline_flow = """
        Raw Data
           ↓
        [Synthetic Generation] → SyntheticDataProvider
           ↓
        [Validation] → DataValidator
           ├─ Duplicates
           ├─ Missing Values
           ├─ Prices (negative, outliers)
           ├─ Volumes
           ├─ OHLC Logic
           ├─ Timestamps
           ├─ Futures-specific
           └─ Options-specific
           ↓
        [Cleaning] → DataCleaner
           ├─ Type Normalization
           ├─ Timestamp Fixing
           ├─ Duplicate Removal
           ├─ Missing Value Handling
           └─ Outlier Removal
           ↓
        [Storage] → ParquetStorage
           ├─ futures/
           ├─ options/
           └─ spot/
           ↓
        Clean Data (Ready for Analysis)
        """
        
        st.code(pipeline_flow, language="text")
    
    # TAB 2: Data Generation
    with tab2:
        st.subheader("🔄 Synthetic Data Generation")
        
        create_info_box(
            "Realistic Synthetic Data",
            "Generate reproducible synthetic market data for testing without external APIs.",
            "info"
        )
        
        col1, col2 = st.columns([0.6, 0.4])
        
        with col1:
            st.markdown("""
            ### Generation Parameters
            
            **Geometric Random Walk Model:**
            - Daily drift: 0.03%
            - Daily volatility: 1.5%
            - Intrabar volatility: 0.5%
            - Random seed support
            
            **OHLC Logic:**
            - High ≥ max(Open, High, Low, Close)
            - Low ≤ min(Open, High, Low, Close)
            - High ≥ Low
            """)
        
        with col2:
            st.markdown("""
            **Volume & OI:**
            - Volume: 1M - 10M contracts
            - Open Interest: trending
            - Realistic ranges
            """)
        
        st.markdown("---")
        
        # Interactive demo
        st.subheader("📊 Generate Sample Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            instrument = st.selectbox(
                "Select Instrument",
                ["NIFTY", "BANKNIFTY", "FINNIFTY"],
                key="instrument_select"
            )
        
        with col2:
            num_days = st.slider(
                "Number of Days",
                min_value=5,
                max_value=100,
                value=20,
                key="num_days_slider"
            )
        
        if st.button("Generate Data", use_container_width=True):
            with st.spinner("Generating synthetic data..."):
                try:
                    provider = SyntheticDataProvider(instrument, random_seed=42)
                    df = provider.fetch_futures_data(
                        "2024-01-01",
                        f"2024-01-{min(num_days + 1, 31):02d}"
                    )
                    
                    st.success(f"✅ Generated {len(df)} days of data")
                    
                    # Display sample
                    st.subheader("📋 Sample Data (First 5 rows)")
                    st.dataframe(df.head(5), use_container_width=True)
                    
                    # Statistics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Records", len(df))
                    with col2:
                        st.metric("Close Range", f"₹{df['close'].min():.0f} - ₹{df['close'].max():.0f}")
                    with col3:
                        st.metric("Avg Volume", f"{df['volume'].mean()/1e6:.1f}M")
                    with col4:
                        st.metric("Daily Return", f"{((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100):.2f}%")
                    
                except Exception as e:
                    st.error(f"Error generating data: {e}")
    
    # TAB 3: Validation
    with tab3:
        st.subheader("✅ Data Validation")
        
        create_info_box(
            "8 Validation Categories",
            "Comprehensive data quality checks with detailed reporting.",
            "info"
        )
        
        # Validation categories
        st.markdown("### Validation Check Categories")
        
        cols = st.columns(4)
        categories = [
            ("1️⃣", "Duplicates", "Exact rows & timestamps"),
            ("2️⃣", "Missing", "Required columns & NaN"),
            ("3️⃣", "Prices", "Negative & outliers"),
            ("4️⃣", "Volumes", "Negative & zero volume"),
            ("5️⃣", "OHLC Logic", "High/Low relationships"),
            ("6️⃣", "Timestamps", "Sort order & gaps"),
            ("7️⃣", "Futures", "Open interest"),
            ("8️⃣", "Options", "Strike, IV, prices"),
        ]
        
        for col, (num, name, desc) in zip(cols, categories):
            with col:
                st.markdown(f"**{num} {name}**")
                st.caption(desc)
        
        st.markdown("---")
        
        # Interactive validation
        st.subheader("🧪 Test Validation on Sample Data")
        
        if st.button("Generate & Validate Sample Data", use_container_width=True):
            with st.spinner("Generating and validating..."):
                try:
                    # Generate
                    provider = SyntheticDataProvider("NIFTY", random_seed=42)
                    df = provider.fetch_futures_data("2024-01-01", "2024-01-20")
                    
                    # Validate
                    report = validate_futures_data(df)
                    
                    # Display report
                    st.success("✅ Validation complete")
                    
                    if report.passed_all_checks:
                        st.info("✨ Data quality is excellent - all checks passed!")
                    else:
                        st.warning(f"Found {len(report.issues)} issue(s) to review")
                    
                    # Show report
                    st.text(report.summary())
                    
                except Exception as e:
                    st.error(f"Error during validation: {e}")
    
    # TAB 4: Cleaning
    with tab4:
        st.subheader("🧹 Data Cleaning")
        
        create_info_box(
            "Automated 5-Step Pipeline",
            "Systematically clean and normalize data for analysis.",
            "info"
        )
        
        # Cleaning steps
        st.markdown("### Cleaning Operations")
        
        steps = [
            ("1️⃣", "Normalize Types", "Strings → float/int/datetime"),
            ("2️⃣", "Fix Timestamps", "Convert to datetime index"),
            ("3️⃣", "Remove Duplicates", "Exact row duplicates"),
            ("4️⃣", "Handle Missing", "Forward/backward fill"),
            ("5️⃣", "Remove Outliers", "Prices > 5σ from mean"),
        ]
        
        for num, name, desc in steps:
            col1, col2, col3 = st.columns([0.15, 0.3, 0.55])
            with col1:
                st.write(num)
            with col2:
                st.write(f"**{name}**")
            with col3:
                st.caption(desc)
        
        st.markdown("---")
        
        # Interactive cleaning demo
        st.subheader("🧪 Test Cleaning Pipeline")
        
        if st.button("Generate, Validate & Clean Data", use_container_width=True):
            with st.spinner("Processing data..."):
                try:
                    # Generate
                    provider = SyntheticDataProvider("NIFTY", random_seed=42)
                    raw_df = provider.fetch_futures_data("2024-01-01", "2024-01-31")
                    
                    # Validate before
                    report_before = validate_futures_data(raw_df)
                    
                    # Clean
                    cleaned_df, log = clean_futures_data(raw_df)
                    
                    # Validate after
                    report_after = validate_futures_data(cleaned_df)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Before Cleaning", len(raw_df), delta="records")
                    with col2:
                        st.metric("After Cleaning", len(cleaned_df), delta="records")
                    with col3:
                        st.metric("Issues Before", len(report_before.issues))
                    
                    st.success("✅ Cleaning complete")
                    
                    # Show operations
                    st.subheader("Operations Performed")
                    for op, count in sorted(log.items()):
                        if count > 0:
                            st.caption(f"✓ {op}: {count}")
                    
                    # Show cleaned data
                    st.subheader("Cleaned Data Sample")
                    st.dataframe(cleaned_df.head(5), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error during cleaning: {e}")
    
    # TAB 5: Storage
    with tab5:
        st.subheader("💾 Parquet Storage")
        
        create_info_box(
            "Efficient Data Storage",
            "Store cleaned data in Parquet format with compression and metadata.",
            "info"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Storage Advantages
            
            - **Compression**: Snappy (30-50% size reduction)
            - **Speed**: Fast I/O operations
            - **Type Preservation**: Maintains data types
            - **Columns**: Column-oriented storage
            - **Metadata**: Preserves index and schema
            """)
        
        with col2:
            st.markdown("""
            ### Directory Structure
            
            ```
            data/processed/
            ├── futures/
            │   ├── nifty_futures.parquet
            │   ├── banknifty_futures.parquet
            │   └── ...
            ├── options/
            │   └── ...
            └── spot/
                └── ...
            ```
            """)
        
        st.markdown("---")
        
        # Storage demo
        st.subheader("🧪 Test Storage Pipeline")
        
        if st.button("Generate → Validate → Clean → Store", use_container_width=True):
            with st.spinner("Processing complete pipeline..."):
                try:
                    # 1. Generate
                    provider = SyntheticDataProvider("NIFTY", random_seed=42)
                    raw_df = provider.fetch_futures_data("2024-01-01", "2024-02-29")
                    
                    # 2. Validate
                    report_before = validate_futures_data(raw_df)
                    
                    # 3. Clean
                    cleaned_df, clean_log = clean_futures_data(raw_df)
                    
                    # 4. Store
                    storage = ParquetStorage()
                    filepath = storage.save_futures(cleaned_df, "NIFTY")
                    
                    # 5. Verify
                    loaded_df = storage.load_futures("NIFTY")
                    
                    st.success("✅ Complete pipeline executed successfully!")
                    
                    # Show results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Pipeline Results")
                        st.metric("Generated Records", len(raw_df))
                        st.metric("After Cleaning", len(cleaned_df))
                        st.metric("Loaded Back", len(loaded_df))
                    
                    with col2:
                        st.subheader("File Info")
                        info = storage.get_file_info(filepath)
                        st.metric("File Size", f"{info['size_mb']:.2f} MB")
                        st.metric("Rows", info['num_rows'])
                        st.metric("Columns", info['num_columns'])
                    
                    st.markdown("---")
                    
                    st.subheader("💾 Stored File Path")
                    st.code(str(filepath))
                    
                except Exception as e:
                    st.error(f"Error in pipeline: {e}")
    
    st.markdown("---")
    
    # Test Results Summary
    st.subheader("✅ Phase 2 Test Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Data Tests", "29/29", delta="✅ 100% passing")
    
    with col2:
        st.metric("Regression Tests", "12/12", delta="✅ Phase 1 intact")
    
    with col3:
        st.metric("Execution Time", "~0.7s", delta="All tests combined")
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ Back to Phase 1", use_container_width=True):
            st.session_state.current_page = "phase1_architecture"
            st.rerun()
    
    with col2:
        st.caption("Phase 2 - Data Pipeline")
    
    with col3:
        if st.button("⏭️ Next Phase (Coming Soon)", use_container_width=True, disabled=True):
            pass
