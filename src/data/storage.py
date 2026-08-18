"""
Data storage module for DerivaLens.

Handles saving and loading data in Parquet format.

Parquet advantages:
- Efficient compression
- Preserves data types
- Fast read/write
- Supports large datasets
- Column-oriented (good for analytics)
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

import pandas as pd
import pyarrow.parquet as pq
from loguru import logger


class ParquetStorage:
    """
    Manages Parquet file storage for futures and options data.
    """
    
    def __init__(self, base_path: Path | str | None = None):
        """
        Initialize storage.
        
        Args:
            base_path: Base directory for data storage.
                      If None, uses data/processed from config.
        """
        if base_path is None:
            from src.config import get_config
            config = get_config()
            base_path = config.get('data.processed_dir')
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.futures_path = self.base_path / 'futures'
        self.options_path = self.base_path / 'options'
        self.spot_path = self.base_path / 'spot'
        
        for path in [self.futures_path, self.options_path, self.spot_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_futures(
        self,
        df: pd.DataFrame,
        instrument: str,
        expiry: Optional[str] = None,
        overwrite: bool = False
    ) -> Path:
        """
        Save futures data to Parquet.
        
        Args:
            df: DataFrame with futures data
            instrument: Instrument name (e.g., 'NIFTY')
            expiry: Expiry date (optional, for contract-specific storage)
            overwrite: Whether to overwrite existing file
        
        Returns:
            Path to saved file
        """
        filename = self._get_filename('futures', instrument, expiry)
        filepath = self.futures_path / filename
        
        return self._save_parquet(df, filepath, overwrite)
    
    def save_options(
        self,
        df: pd.DataFrame,
        instrument: str,
        expiry: Optional[str] = None,
        overwrite: bool = False
    ) -> Path:
        """
        Save options data to Parquet.
        
        Args:
            df: DataFrame with options chain data
            instrument: Instrument name (e.g., 'NIFTY')
            expiry: Expiry date (optional)
            overwrite: Whether to overwrite existing file
        
        Returns:
            Path to saved file
        """
        filename = self._get_filename('options', instrument, expiry)
        filepath = self.options_path / filename
        
        return self._save_parquet(df, filepath, overwrite)
    
    def save_spot(
        self,
        df: pd.DataFrame,
        instrument: str,
        overwrite: bool = False
    ) -> Path:
        """
        Save spot/underlying data to Parquet.
        
        Args:
            df: DataFrame with spot data
            instrument: Instrument name (e.g., 'NIFTY')
            overwrite: Whether to overwrite existing file
        
        Returns:
            Path to saved file
        """
        filename = f"{instrument.lower()}_spot.parquet"
        filepath = self.spot_path / filename
        
        return self._save_parquet(df, filepath, overwrite)
    
    def load_futures(
        self,
        instrument: str,
        expiry: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load futures data from Parquet.
        
        Args:
            instrument: Instrument name
            expiry: Expiry date (optional)
        
        Returns:
            DataFrame with futures data
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filename = self._get_filename('futures', instrument, expiry)
        filepath = self.futures_path / filename
        
        return self._load_parquet(filepath)
    
    def load_options(
        self,
        instrument: str,
        expiry: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load options data from Parquet.
        
        Args:
            instrument: Instrument name
            expiry: Expiry date (optional)
        
        Returns:
            DataFrame with options chain data
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filename = self._get_filename('options', instrument, expiry)
        filepath = self.options_path / filename
        
        return self._load_parquet(filepath)
    
    def load_spot(self, instrument: str) -> pd.DataFrame:
        """
        Load spot data from Parquet.
        
        Args:
            instrument: Instrument name
        
        Returns:
            DataFrame with spot data
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filename = f"{instrument.lower()}_spot.parquet"
        filepath = self.spot_path / filename
        
        return self._load_parquet(filepath)
    
    def list_files(self, data_type: str = 'futures') -> list[Path]:
        """
        List all stored files of a given type.
        
        Args:
            data_type: 'futures', 'options', or 'spot'
        
        Returns:
            List of file paths
        """
        if data_type == 'futures':
            path = self.futures_path
        elif data_type == 'options':
            path = self.options_path
        elif data_type == 'spot':
            path = self.spot_path
        else:
            raise ValueError(f"Unknown data_type: {data_type}")
        
        return sorted(path.glob('*.parquet'))
    
    def get_file_info(self, filepath: Path) -> Dict:
        """
        Get information about a Parquet file.
        
        Args:
            filepath: Path to Parquet file
        
        Returns:
            Dict with file info
        """
        table = pq.read_table(filepath)
        
        return {
            'file': filepath.name,
            'size_mb': filepath.stat().st_size / (1024 * 1024),
            'num_rows': table.num_rows,
            'num_columns': table.num_columns,
            'columns': table.column_names,
            'schema': str(table.schema),
        }
    
    def _save_parquet(self, df: pd.DataFrame, filepath: Path, overwrite: bool = False) -> Path:
        """Internal method to save Parquet file."""
        if filepath.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {filepath}. Set overwrite=True to replace.")
        
        df.to_parquet(filepath, index=True, compression='snappy')
        logger.info(f"Saved {len(df)} records to {filepath.name}")
        
        return filepath
    
    def _load_parquet(self, filepath: Path) -> pd.DataFrame:
        """Internal method to load Parquet file."""
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        df = pd.read_parquet(filepath)
        logger.info(f"Loaded {len(df)} records from {filepath.name}")
        
        # Ensure datetime index if present
        if df.index.name == 'datetime' or 'datetime' in str(df.index):
            df.index = pd.to_datetime(df.index)
        
        return df
    
    def _get_filename(
        self,
        data_type: str,
        instrument: str,
        expiry: Optional[str] = None
    ) -> str:
        """Generate filename for data file."""
        if expiry:
            filename = f"{instrument.lower()}_{expiry}_{data_type}.parquet"
        else:
            filename = f"{instrument.lower()}_{data_type}.parquet"
        
        return filename


# Convenience functions
def save_futures(
    df: pd.DataFrame,
    instrument: str,
    base_path: Optional[Path | str] = None
) -> Path:
    """
    Quickly save futures data.
    
    Args:
        df: Futures DataFrame
        instrument: Instrument name
        base_path: Storage path (uses config default if None)
    
    Returns:
        Path to saved file
    """
    storage = ParquetStorage(base_path)
    return storage.save_futures(df, instrument, overwrite=True)


def load_futures(
    instrument: str,
    base_path: Optional[Path | str] = None
) -> pd.DataFrame:
    """
    Quickly load futures data.
    
    Args:
        instrument: Instrument name
        base_path: Storage path (uses config default if None)
    
    Returns:
        Futures DataFrame
    """
    storage = ParquetStorage(base_path)
    return storage.load_futures(instrument)


if __name__ == '__main__':
    print("DerivaLens Parquet Storage Module")
    print("=" * 60)
    print("\nUsage example:")
    print("  from src.data.storage import ParquetStorage")
    print("  storage = ParquetStorage()")
    print("  storage.save_futures(df, 'NIFTY')")
    print("  loaded_df = storage.load_futures('NIFTY')")
