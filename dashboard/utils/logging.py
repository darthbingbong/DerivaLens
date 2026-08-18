"""
Logging utilities for Streamlit app.

Provides logging configuration and utilities for the dashboard.
"""

import streamlit as st
from loguru import logger
import sys
from pathlib import Path


def setup_streamlit_logging():
    """Configure logging for Streamlit app."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure loguru
    logger.add(
        log_dir / "dashboard.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        rotation="500 MB",
    )


def log_page_view(page_name: str):
    """Log page view."""
    logger.info(f"Page viewed: {page_name}")


def log_action(action: str, details: str = ""):
    """Log user action."""
    msg = f"Action: {action}"
    if details:
        msg += f" | Details: {details}"
    logger.info(msg)


def log_error(error: str, page: str = ""):
    """Log error."""
    msg = f"Error: {error}"
    if page:
        msg += f" | Page: {page}"
    logger.error(msg)


def create_debug_info():
    """Create debug information display for development."""
    with st.expander("🐛 Debug Info (Development Only)"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Session State")
            st.write(st.session_state)
        
        with col2:
            st.subheader("Cache Info")
            st.write(f"Cache size: {len(st.session_state)}")
            
            if st.button("Clear Cache"):
                st.session_state.clear()
                st.success("Cache cleared!")
                st.rerun()
