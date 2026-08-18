"""
Data cleaning module for DerivaLens.

Cleans and prepares raw data for analysis:
- Remove or handle duplicates
- Handle missing values
- Fix timestamp issues
- Remove extreme outliers (configurable)
- Normalize data types
"""

from __future__ import annotations

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from loguru import logger


class DataCleaner:
    """
    Cleans futures and options data.
    
    Operations:
    - Remove duplicates
    - Handle missing values
    - Fix timestamps
    - Remove outliers
    - Normalize types
    """
    
    def __init__(self, data_type: str = 'futures'):
        """
        Initialize cleaner.
        
        Args:
            data_type: 'futures' or 'options'
        """
        self.data_type = data_type
        self.outlier_std = 5.0
    
    def clean(
        self,
        df: pd.DataFrame,
        remove_duplicates: bool = True,
        handle_missing: bool = True,
        remove_outliers: bool = True,
        fix_timestamps: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Run all cleaning operations.
        
        Args:
            df: Raw DataFrame
            remove_duplicates: Remove duplicate rows
            handle_missing: Fill or remove missing values
            remove_outliers: Remove extreme outliers
            fix_timestamps: Ensure datetime index and sort
        
        Returns:
            Tuple of (cleaned_df, operations_log)
        """
        operations_log: Dict[str, int] = {}
        
        logger.info(f"Starting data cleaning on {len(df)} records")
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Normalize types FIRST so we can work with numeric data
        df, type_ops = self._normalize_types(df)
        operations_log.update(type_ops)
        
        if fix_timestamps:
            df, ts_ops = self._fix_timestamps(df)
            operations_log.update(ts_ops)
        
        if remove_duplicates:
            df, dup_ops = self._remove_duplicates(df)
            operations_log.update(dup_ops)
        
        if handle_missing:
            df, miss_ops = self._handle_missing_values(df)
            operations_log.update(miss_ops)
        
        if remove_outliers:
            df, out_ops = self._remove_outliers(df)
            operations_log.update(out_ops)
        
        logger.info(f"Cleaning complete: {len(df)} records remain")
        logger.debug(f"Operations: {operations_log}")
        
        return df, operations_log
    
    def _fix_timestamps(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Fix timestamp issues."""
        log = {}
        
        # Convert datetime column to index if present
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            df = df.set_index('datetime')
            log['datetime_converted'] = 1
        
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index, errors='coerce')
                log['index_converted_to_datetime'] = 1
            except Exception as e:
                logger.warning(f"Could not convert index to datetime: {e}")
        
        # Remove rows with NaT index (failed conversions)
        nat_count = df.index.isna().sum()
        if nat_count > 0:
            df = df[df.index.notna()]
            log['removed_nat_index'] = nat_count
        
        # Sort by datetime
        df = df.sort_index()
        log['sorted_by_timestamp'] = 1
        
        return df, log
    
    def _remove_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Remove duplicate records."""
        log = {}
        
        initial_len = len(df)
        
        # Remove exact duplicates
        df = df.drop_duplicates()
        duplicates_removed = initial_len - len(df)
        
        if duplicates_removed > 0:
            log['exact_duplicates_removed'] = duplicates_removed
            logger.info(f"Removed {duplicates_removed} exact duplicate rows")
        
        return df, log
    
    def _handle_missing_values(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Handle missing values."""
        log = {}
        
        price_cols = ['open', 'high', 'low', 'close']
        
        for col in price_cols:
            if col not in df.columns:
                continue
            
            missing = df[col].isna().sum()
            if missing == 0:
                continue
            
            # For price data, forward fill then backward fill
            # This is reasonable for missing prices (short gaps)
            df[col] = df[col].ffill()
            df[col] = df[col].bfill()
            
            # If still missing, drop those rows
            still_missing = df[col].isna().sum()
            if still_missing > 0:
                df = df[df[col].notna()]
                log[f'{col}_missing_removed'] = still_missing
                logger.warning(f"Removed {still_missing} rows with missing {col}")
        
        # For volume and OI, fill with 0 (no trading)
        for col in ['volume', 'open_interest']:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    df[col] = df[col].fillna(0)
                    log[f'{col}_filled_with_zero'] = missing_count
        
        return df, log
    
    def _remove_outliers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Remove extreme outliers."""
        log = {}
        
        price_cols = ['close']  # Only check close price for outliers
        
        for col in price_cols:
            if col not in df.columns:
                continue
            
            if len(df) < 2:
                continue
            
            # Calculate z-score
            mean = df[col].mean()
            std = df[col].std()
            
            if std == 0:
                continue
            
            z_scores = np.abs((df[col] - mean) / std)
            outliers = z_scores > self.outlier_std
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                df = df[~outliers]
                log[f'{col}_outliers_removed'] = outlier_count
                logger.info(f"Removed {outlier_count} outliers from {col}")
        
        return df, log
    
    def _normalize_types(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Normalize data types."""
        log = {}
        
        # Convert price columns to float64 (explicitly)
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
                log[f'{col}_to_float'] = 1
        
        # Convert volume to int64
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').astype('int64')
            log['volume_to_int64'] = 1
        
        # Convert OI to int64
        if 'open_interest' in df.columns:
            df['open_interest'] = pd.to_numeric(df['open_interest'], errors='coerce').astype('int64')
            log['open_interest_to_int64'] = 1
        
        return df, log
    
    def get_cleaning_summary(self, operations_log: Dict[str, int]) -> str:
        """Generate human-readable cleaning summary."""
        lines = [
            f"\n{'=' * 70}",
            f"Data Cleaning Summary",
            f"{'=' * 70}",
        ]
        
        if not operations_log:
            lines.append("No cleaning operations needed")
        else:
            for operation, count in operations_log.items():
                if count > 0:
                    lines.append(f"  • {operation}: {count}")
        
        lines.append(f"{'=' * 70}\n")
        return "\n".join(lines)


# Convenience functions
def clean_futures_data(
    df: pd.DataFrame,
    remove_outliers: bool = True
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Clean futures data with sensible defaults.
    
    Args:
        df: Raw futures DataFrame
        remove_outliers: Whether to remove extreme outliers
    
    Returns:
        Tuple of (cleaned_df, operations_log)
    """
    cleaner = DataCleaner('futures')
    return cleaner.clean(df, remove_outliers=remove_outliers)


def clean_options_data(
    df: pd.DataFrame,
    remove_outliers: bool = True
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Clean options data with sensible defaults.
    
    Args:
        df: Raw options DataFrame
        remove_outliers: Whether to remove extreme outliers
    
    Returns:
        Tuple of (cleaned_df, operations_log)
    """
    cleaner = DataCleaner('options')
    return cleaner.clean(df, remove_outliers=remove_outliers)


if __name__ == '__main__':
    print("DerivaLens Data Cleaning Module")
    print("=" * 60)
    print("\nUsage example:")
    print("  from src.data.cleaning import clean_futures_data")
    print("  cleaned_df, log = clean_futures_data(df)")
    print("  print(log)")
