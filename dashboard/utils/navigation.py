"""
Navigation management for DerivaLens dashboard.

Handles page routing and session state management.
"""

import streamlit as st
from typing import Dict, List, Tuple


class NavigationManager:
    """Manages navigation between different pages and phases."""
    
    def __init__(self):
        """Initialize navigation manager."""
        self.pages = self._setup_pages()
        self.current_page = st.session_state.get("current_page", "phase1_architecture")
    
    def _setup_pages(self) -> Dict[str, Dict[str, str]]:
        """Setup page metadata."""
        return {
            # Foundation Phases
            "phase1_architecture": {
                "title": "📋 Phase 1: Project Architecture",
                "phase": 1,
                "section": "Foundation",
                "status": "✅ Complete",
                "description": "Project configuration, structure, and setup"
            },
            "phase2_data_pipeline": {
                "title": "📥 Phase 2: Data Pipeline",
                "phase": 2,
                "section": "Foundation",
                "status": "✅ Complete",
                "description": "Data ingestion, validation, and cleaning"
            },
            
            # Analysis Phases
            "phase3_futures": {
                "title": "📈 Phase 3: Futures Processing",
                "phase": 3,
                "section": "Analysis",
                "status": "⏳ In Progress",
                "description": "Futures-specific calculations and analysis"
            },
            "phase4_options": {
                "title": "📊 Phase 4: Options Processing",
                "phase": 4,
                "section": "Analysis",
                "status": "⏳ Upcoming",
                "description": "Options chain processing and Greeks"
            },
            "phase5_volatility": {
                "title": "📉 Phase 5: Volatility Analysis",
                "phase": 5,
                "section": "Analysis",
                "status": "⏳ Upcoming",
                "description": "Volatility estimation and analysis"
            },
            "phase6_regimes": {
                "title": "🔄 Phase 6: Regime Detection",
                "phase": 6,
                "section": "Analysis",
                "status": "⏳ Upcoming",
                "description": "Market regime classification"
            },
            
            # Strategy Phases
            "phase7_strategies": {
                "title": "🎯 Phase 7: Strategy Development",
                "phase": 7,
                "section": "Strategy",
                "status": "⏳ Upcoming",
                "description": "Trading strategy implementation"
            },
            "phase8_backtesting": {
                "title": "🧪 Phase 8: Backtesting",
                "phase": 8,
                "section": "Strategy",
                "status": "⏳ Upcoming",
                "description": "Historical performance testing"
            },
            "phase9_risk": {
                "title": "⚠️ Phase 9: Risk Analysis",
                "phase": 9,
                "section": "Strategy",
                "status": "⏳ Upcoming",
                "description": "Risk metrics and management"
            },
            "phase10_walkforward": {
                "title": "🔁 Phase 10: Walk-Forward Validation",
                "phase": 10,
                "section": "Strategy",
                "status": "⏳ Upcoming",
                "description": "Out-of-sample validation"
            },
            
            # Reporting Phases
            "phase11_statistics": {
                "title": "📊 Phase 11: Statistical Analysis",
                "phase": 11,
                "section": "Reporting",
                "status": "⏳ Upcoming",
                "description": "Performance statistics and metrics"
            },
            "phase12_dashboard": {
                "title": "🎨 Phase 12: Interactive Dashboard",
                "phase": 12,
                "section": "Reporting",
                "status": "⏳ Upcoming",
                "description": "Real-time performance monitoring"
            },
            "phase13_reports": {
                "title": "📄 Phase 13: Report Generation",
                "phase": 13,
                "section": "Reporting",
                "status": "⏳ Upcoming",
                "description": "Research and performance reports"
            },
            "phase14_polish": {
                "title": "✨ Phase 14: Polish & Finalization",
                "phase": 14,
                "section": "Reporting",
                "status": "⏳ Upcoming",
                "description": "Documentation and final touches"
            },
        }
    
    def get_page_info(self, page_key: str) -> Dict[str, str]:
        """Get metadata for a specific page."""
        return self.pages.get(page_key, {})
    
    def get_pages_by_section(self, section: str) -> List[Tuple[str, Dict]]:
        """Get all pages in a specific section."""
        return [
            (key, page) for key, page in self.pages.items()
            if page.get("section") == section
        ]
    
    def is_page_available(self, page_key: str) -> bool:
        """Check if a page is implemented and available."""
        available_pages = ["phase1_architecture", "phase2_data_pipeline"]
        return page_key in available_pages
    
    def get_phase_progress(self) -> Dict[str, int]:
        """Get completion statistics by phase."""
        stats = {
            "completed": 0,
            "in_progress": 0,
            "upcoming": 0,
            "total": 0
        }
        
        for page in self.pages.values():
            stats["total"] += 1
            if "✅" in page["status"]:
                stats["completed"] += 1
            elif "⏳ In Progress" in page["status"]:
                stats["in_progress"] += 1
            else:
                stats["upcoming"] += 1
        
        return stats


def create_phase_breadcrumb(current_phase: int):
    """Create a breadcrumb showing current phase."""
    phases = list(range(1, 15))
    phase_status = []
    
    for p in phases:
        if p < current_phase:
            phase_status.append("✅")
        elif p == current_phase:
            phase_status.append("▶️")
        else:
            phase_status.append("⏳")
    
    breadcrumb = " → ".join([f"Phase {p} {phase_status[p-1]}" for p in phases])
    st.caption(breadcrumb)
