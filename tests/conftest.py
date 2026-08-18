"""
Pytest configuration and fixtures for DerivaLens tests.
"""

import pytest
from pathlib import Path
from src.config import Config


@pytest.fixture
def config():
    """Provide a config instance for tests."""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    return Config(config_path)


@pytest.fixture
def temp_data_dir(tmp_path):
    """Provide a temporary data directory for tests."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    features_dir = tmp_path / "features"
    
    raw_dir.mkdir()
    processed_dir.mkdir()
    features_dir.mkdir()
    
    return {
        'root': tmp_path,
        'raw': raw_dir,
        'processed': processed_dir,
        'features': features_dir
    }


@pytest.fixture
def sample_dates():
    """Provide sample date ranges for testing."""
    import pandas as pd
    return {
        'start': pd.Timestamp('2023-01-01'),
        'end': pd.Timestamp('2023-12-31'),
        'dates': pd.date_range('2023-01-01', '2023-12-31', freq='D')
    }
