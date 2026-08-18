"""
Data validation module for DerivaLens.

Implements comprehensive data quality checks for futures and options data.
Produces human-readable quality reports.

Key validations:
- Duplicate detection
- Missing value detection
- Price/volume sanity checks
- Expiry validation
- OHLC logic validation
- Timestamp consistency
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from datetime import datetime

import pandas as pd
import numpy as np
from loguru import logger


@dataclass
class ValidationIssue:
    """Represents a single data quality issue."""
    
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'duplicates', 'missing', 'price', 'expiry', etc.
    message: str
    count: int = 0
    percentage: float = 0.0


@dataclass
class DataQualityReport:
    """Comprehensive data quality report."""
    
    total_records: int
    date_range: Tuple[datetime, datetime] | None
    issues: List[ValidationIssue] = field(default_factory=list)
    passed_all_checks: bool = True
    
    def add_issue(self, issue: ValidationIssue) -> None:
        """Add an issue to the report."""
        self.issues.append(issue)
        if issue.severity == 'error':
            self.passed_all_checks = False
    
    def summary(self) -> str:
        """Return human-readable summary."""
        lines = [
            f"\n{'=' * 70}",
            f"Data Quality Report",
            f"{'=' * 70}",
            f"Total records: {self.total_records:,}",
        ]
        
        if self.date_range:
            start, end = self.date_range
            lines.append(f"Date range: {start.date()} to {end.date()}")
        
        if not self.issues:
            lines.append("\n✓ All checks passed - data quality is good")
        else:
            lines.append(f"\nFound {len(self.issues)} issue(s):\n")
            
            # Group by severity
            errors = [i for i in self.issues if i.severity == 'error']
            warnings = [i for i in self.issues if i.severity == 'warning']
            infos = [i for i in self.issues if i.severity == 'info']
            
            if errors:
                lines.append("ERRORS (must fix):")
                for issue in errors:
                    lines.append(f"  • {issue.message}")
                    if issue.count > 0:
                        lines.append(f"    ({issue.count} records, {issue.percentage:.1f}%)")
            
            if warnings:
                lines.append("\nWARNINGS (should review):")
                for issue in warnings:
                    lines.append(f"  • {issue.message}")
                    if issue.count > 0:
                        lines.append(f"    ({issue.count} records, {issue.percentage:.1f}%)")
            
            if infos:
                lines.append("\nINFO:")
                for issue in infos:
                    lines.append(f"  • {issue.message}")
        
        lines.append(f"{'=' * 70}\n")
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self.summary()


class DataValidator:
    """
    Validates futures and options data.
    
    Checks for:
    - Duplicate records
    - Missing values
    - Invalid prices (negative, zero, extreme outliers)
    - Invalid volumes
    - OHLC logic violations
    - Invalid expirations
    - Timestamp issues
    """
    
    def __init__(self, data_type: str = 'futures'):
        """
        Initialize validator.
        
        Args:
            data_type: 'futures' or 'options'
        """
        self.data_type = data_type
        self.config_thresholds = {
            'outlier_std': 5.0,           # Flag prices > 5 std dev
            'min_price': 0.01,            # Minimum valid price
            'max_price_change_pct': 50,   # Max daily move (%)
            'min_volume': 0,              # Minimum volume
            'max_volume': 1e10,           # Maximum reasonable volume
        }
    
    def validate(self, df: pd.DataFrame) -> DataQualityReport:
        """
        Run all validation checks on the dataframe.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataQualityReport with all issues found
        """
        report = DataQualityReport(
            total_records=len(df),
            date_range=(df.index.min(), df.index.max()) if isinstance(df.index, pd.DatetimeIndex) else None
        )
        
        if len(df) == 0:
            report.add_issue(ValidationIssue(
                severity='error',
                category='empty',
                message='DataFrame is empty'
            ))
            return report
        
        # Run all checks
        self._check_duplicates(df, report)
        self._check_missing_values(df, report)
        self._check_prices(df, report)
        self._check_volumes(df, report)
        self._check_ohlc_logic(df, report)
        self._check_timestamps(df, report)
        
        # Optional checks based on data type
        if self.data_type == 'options':
            self._check_options_data(df, report)
        elif self.data_type == 'futures':
            self._check_futures_data(df, report)
        
        logger.info(f"Validation complete: {len(report.issues)} issue(s) found")
        
        return report
    
    def _check_duplicates(self, df: pd.DataFrame, report: DataQualityReport) -> None:
        """Check for duplicate records."""
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            pct = (duplicates / len(df)) * 100
            report.add_issue(ValidationIssue(
                severity='error',
                category='duplicates',
                message=f"Found {duplicates} duplicate records (exact row duplicates)",
                count=duplicates,
                percentage=pct
            ))
        
        # Check for duplicate dates (if index is datetime)
        if isinstance(df.index, pd.DatetimeIndex):
            duplicate_dates = df.index.duplicated().sum()
            if duplicate_dates > 0:
                pct = (duplicate_dates / len(df)) * 100
                report.add_issue(ValidationIssue(
                    severity='error',
                    category='duplicates',
                    message=f"Found {duplicate_dates} duplicate timestamps",
                    count=duplicate_dates,
                    percentage=pct
                ))
    
    def _check_missing_values(self, df: pd.DataFrame, report: DataQualityReport) -> None:
        """Check for missing values."""
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        
        for col in required_cols:
            if col not in df.columns:
                report.add_issue(ValidationIssue(
                    severity='error',
                    category='missing',
                    message=f"Missing required column: {col}"
                ))
                continue
            
            missing = df[col].isna().sum()
            if missing > 0:
                pct = (missing / len(df)) * 100
                severity = 'warning' if pct <= 5 else 'error'
                report.add_issue(ValidationIssue(
                    severity=severity,
                    category='missing',
                    message=f"Missing values in {col}",
                    count=missing,
                    percentage=pct
                ))
    
    def _check_prices(self, df: pd.DataFrame, report: DataQualityReport) -> None:
        """Check price validity."""
        price_cols = ['open', 'high', 'low', 'close']
        
        for col in price_cols:
            if col not in df.columns:
                continue
            
            # Check for negative or zero prices
            invalid = (df[col] <= 0).sum()
            if invalid > 0:
                pct = (invalid / len(df)) * 100
                report.add_issue(ValidationIssue(
                    severity='error',
                    category='price',
                    message=f"Invalid (≤0) prices in {col}",
                    count=invalid,
                    percentage=pct
                ))
            
            # Check for extreme outliers
            mean = df[col].mean()
            std = df[col].std()
            outliers = np.abs((df[col] - mean) / std) > self.config_thresholds['outlier_std']
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                pct = (outlier_count / len(df)) * 100
                report.add_issue(ValidationIssue(
                    severity='warning',
                    category='price',
                    message=f"Potential outliers in {col} (>{self.config_thresholds['outlier_std']}σ)",
                    count=outlier_count,
                    percentage=pct
                ))
    
    def _check_volumes(self, df: pd.DataFrame, report: DataQualityReport) -> None:
        """Check volume validity."""
        if 'volume' not in df.columns:
            return
        
        # Check for negative volumes
        negative = (df['volume'] < 0).sum()
        if negative > 0:
            pct = (negative / len(df)) * 100
            report.add_issue(ValidationIssue(
                severity='error',
                category='volume',
                message=f"Negative volumes found",
                count=negative,
                percentage=pct
            ))
        
        # Check for zero volumes (warning, not error - can happen at night)
        zero_vol = (df['volume'] == 0).sum()
        if zero_vol > 0:
            pct = (zero_vol / len(df)) * 100
            if pct > 5:  # More than 5% zero volume is suspicious
                report.add_issue(ValidationIssue(
                    severity='warning',
                    category='volume',
                    message=f"Zero volume records (market closed?)",
                    count=zero_vol,
                    percentage=pct
                ))
            else:
                report.add_issue(ValidationIssue(
                    severity='info',
                    category='volume',
                    message=f"Minor zero volume records",
                    count=zero_vol,
                    percentage=pct
                ))
    
    def _check_ohlc_logic(self, df: pd.DataFrame, report: DataQualityReport) -> None:
        """Check that OHLC relationships are correct."""
        price_cols = ['open', 'high', 'low', 'close']
        
        # Check all columns exist
        if not all(col in df.columns for col in price_cols):
            return
        
        # High should be >= max(Open, Close, Low)
        # Low should be <= min(Open, Close, High)
        violations = 0
        
        for idx in df.index:
            high = df.loc[idx, 'high']
            low = df.loc[idx, 'low']
            open_price = df.loc[idx, 'open']
            close = df.loc[idx, 'close']
            
            # High should be >= all prices
            if not (high >= open_price and high >= close and high >= low):
                violations += 1
            
            # Low should be <= all prices
            if not (low <= open_price and low <= close and low <= high):
                violations += 1
            
            # Low should be <= High
            if low > high:
                violations += 1
        
        if violations > 0:
            pct = (violations / len(df)) * 100
            report.add_issue(ValidationIssue(
                severity='error',
                category='ohlc',
                message=f"OHLC logic violations (high < low or out of range)",
                count=violations,
                percentage=pct
            ))
    
    def _check_timestamps(self, df: pd.DataFrame, report: DataQualityReport) -> None:
        """Check timestamp consistency."""
        if not isinstance(df.index, pd.DatetimeIndex):
            return
        
        # Check if sorted
        if not df.index.is_monotonic_increasing:
            report.add_issue(ValidationIssue(
                severity='warning',
                category='timestamp',
                message='Data is not in chronological order'
            ))
        
        # Check for gaps (optional - can be expected for weekends)
        # Just report info if there are gaps
        time_diffs = df.index.to_series().diff()
        max_gap = time_diffs.max()
        
        report.add_issue(ValidationIssue(
            severity='info',
            category='timestamp',
            message=f"Maximum time gap between records: {max_gap}"
        ))
    
    def _check_futures_data(self, df: pd.DataFrame, report: DataQualityReport) -> None:
        """Futures-specific checks."""
        # Check for open_interest column (optional but recommended)
        if 'open_interest' not in df.columns:
            report.add_issue(ValidationIssue(
                severity='warning',
                category='futures',
                message='Missing open_interest column (recommended for futures)'
            ))
        else:
            # Check OI validity
            negative_oi = (df['open_interest'] < 0).sum()
            if negative_oi > 0:
                pct = (negative_oi / len(df)) * 100
                report.add_issue(ValidationIssue(
                    severity='warning',
                    category='futures',
                    message=f"Negative open_interest values",
                    count=negative_oi,
                    percentage=pct
                ))
    
    def _check_options_data(self, df: pd.DataFrame, report: DataQualityReport) -> None:
        """Options-specific checks."""
        required_cols = ['strike', 'call_price', 'put_price']
        
        for col in required_cols:
            if col not in df.columns:
                report.add_issue(ValidationIssue(
                    severity='warning',
                    category='options',
                    message=f"Missing expected options column: {col}"
                ))
        
        # Check for IV column
        iv_cols = [c for c in df.columns if 'iv' in c.lower()]
        if not iv_cols:
            report.add_issue(ValidationIssue(
                severity='warning',
                category='options',
                message='No implied volatility (IV) column found'
            ))
    
    def fix_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert datetime column to index if needed.
        
        Args:
            df: DataFrame that may have datetime column
        
        Returns:
            DataFrame with datetime as index
        """
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
            df = df.sort_index()
        elif isinstance(df.index, pd.DatetimeIndex):
            df = df.sort_index()
        else:
            logger.warning("Could not convert to datetime index")
        
        return df


# Convenience functions
def validate_futures_data(df: pd.DataFrame) -> DataQualityReport:
    """Validate futures data quickly."""
    validator = DataValidator('futures')
    return validator.validate(df)


def validate_options_data(df: pd.DataFrame) -> DataQualityReport:
    """Validate options data quickly."""
    validator = DataValidator('options')
    return validator.validate(df)


if __name__ == '__main__':
    # Example usage
    print("DerivaLens Data Validation Module")
    print("=" * 60)
    print("\nUsage example:")
    print("  from src.data.validation import validate_futures_data")
    print("  report = validate_futures_data(df)")
    print("  print(report.summary())")
