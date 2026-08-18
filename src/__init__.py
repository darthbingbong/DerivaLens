"""
DerivaLens: Regime-Aware Futures & Options Research Engine

A quantitative research platform for analyzing derivatives markets,
identifying market regimes, and backtesting systematic strategies.

WARNING: This is an educational research tool.
It does NOT provide investment advice or trading recommendations.
Use only with historical data for research purposes.
"""

__version__ = "0.1.0"
__author__ = "Quantitative Research Team"
__description__ = "Regime-Aware Futures & Options Research and Backtesting Engine"

import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Define project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
REPORTS_DIR = PROJECT_ROOT / "reports"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Create directories if they don't exist
for directory in [DATA_DIR, REPORTS_DIR, NOTEBOOKS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "raw").mkdir(exist_ok=True)
    (directory / "processed").mkdir(exist_ok=True)

logger.info("DerivaLens initialized successfully")
