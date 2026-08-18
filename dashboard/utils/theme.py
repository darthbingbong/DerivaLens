"""
Theme and styling utilities for DerivaLens dashboard.

Provides consistent styling, colors, and custom CSS for the Streamlit app.
"""

import streamlit as st


def setup_theme():
    """Configure Streamlit theme settings."""
    st.set_page_config(
        initial_sidebar_state="expanded",
    )


def apply_custom_styling():
    """Apply custom CSS styling to the app."""
    custom_css = """
    <style>
    /* Main title styling */
    .main h1 {
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 10px;
    }
    
    /* Section headers */
    .main h2 {
        color: #2ca02c;
        margin-top: 30px;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    
    /* Success boxes */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 15px;
        border-radius: 5px;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        padding: 15px;
        border-radius: 5px;
    }
    
    /* Warning boxes */
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        padding: 15px;
        border-radius: 5px;
    }
    
    /* Code blocks */
    .code-block {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
    }
    
    /* Sidebar styling */
    .sidebar {
        background-color: #f8f9fa;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: 600;
    }
    
    /* Table styling */
    .streamlit-table {
        font-size: 12px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


class ColorPalette:
    """Color constants for consistent styling."""
    
    PRIMARY = "#1f77b4"
    SUCCESS = "#2ca02c"
    WARNING = "#ff7f0e"
    DANGER = "#d62728"
    INFO = "#17a2b8"
    SECONDARY = "#7f7f7f"
    
    # Semantic colors
    POSITIVE = "#27ae60"
    NEGATIVE = "#e74c3c"
    NEUTRAL = "#95a5a6"
    
    # Chart colors
    CHART_COLORS = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]


def format_metric(value, label, delta=None, delta_color="off"):
    """Format and display a metric with optional delta."""
    st.metric(label, value, delta=delta, delta_color=delta_color)


def create_two_column_metric(col1, col2, metric1, metric2):
    """Create a two-column metric display."""
    with col1:
        st.metric(metric1['label'], metric1['value'], delta=metric1.get('delta'))
    with col2:
        st.metric(metric2['label'], metric2['value'], delta=metric2.get('delta'))


def create_info_box(title, content, box_type="info"):
    """Create a styled info/success/warning box."""
    style_map = {
        "success": ("✅", "#d4edda", "#155724"),
        "warning": ("⚠️", "#fff3cd", "#856404"),
        "info": ("ℹ️", "#d1ecf1", "#004085"),
        "error": ("❌", "#f8d7da", "#721c24"),
    }
    
    emoji, bg_color, text_color = style_map.get(box_type, style_map["info"])
    
    html_string = f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 8px; 
                border-left: 4px solid {text_color};">
        <h4 style="color: {text_color}; margin: 0;">{emoji} {title}</h4>
        <p style="color: {text_color}; margin: 10px 0 0 0;">{content}</p>
    </div>
    """
    st.markdown(html_string, unsafe_allow_html=True)
