"""
Unit tests for data ingestion, validation, cleaning, and storage modules.

Tests:
- Data validation with various quality issues
- Data cleaning operations
- Parquet storage/loading
- Synthetic data generation
"""

import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import pytest
import pandas as pd
import numpy as np

from src.data.validation import (
    DataValidator, DataQualityReport, ValidationIssue,
    validate_futures_data, validate_options_data
)
from src.data.cleaning import DataCleaner, clean_futures_data, clean_options_data
from src.data.storage import ParquetStorage, save_futures, load_futures
from src.data.ingestion import SyntheticDataProvider


class TestDataValidation:
    """Test data validation functionality."""
    
    def test_validation_issue_creation(self):
        """Test ValidationIssue dataclass."""
        issue = ValidationIssue(
            severity='error',
            category='duplicates',
            message='Found duplicates',
            count=5,
            percentage=2.5
        )
        assert issue.severity == 'error'
        assert issue.count == 5
    
    def test_data_quality_report_add_issue(self):
        """Test adding issues to report."""
        report = DataQualityReport(total_records=100, date_range=None)
        assert report.passed_all_checks is True
        
        report.add_issue(ValidationIssue('error', 'test', 'Test error'))
        assert report.passed_all_checks is False
        assert len(report.issues) == 1
    
    def test_validation_duplicates(self):
        """Test duplicate detection."""
        df = pd.DataFrame({
            'close': [100, 100, 101, 102],
        }, index=pd.date_range('2024-01-01', periods=4))
        
        # Add exact duplicate row
        df = pd.concat([df, df.iloc[[0]]])
        
        validator = DataValidator('futures')
        report = validator.validate(df)
        
        assert not report.passed_all_checks
        dup_issues = [i for i in report.issues if i.category == 'duplicates']
        assert len(dup_issues) > 0
    
    def test_validation_missing_values(self):
        """Test missing value detection."""
        df = pd.DataFrame({
            'open': [100, 101, np.nan, 103],
            'high': [102, 103, 104, 105],
            'low': [99, 100, 101, 102],
            'close': [101, 102, 103, 104],
            'volume': [1000, 2000, 3000, 4000],
        }, index=pd.date_range('2024-01-01', periods=4))
        
        validator = DataValidator('futures')
        report = validator.validate(df)
        
        assert not report.passed_all_checks
        missing_issues = [i for i in report.issues if i.category == 'missing']
        assert len(missing_issues) > 0
    
    def test_validation_negative_prices(self):
        """Test negative price detection."""
        df = pd.DataFrame({
            'open': [100, -101, 102, 103],
            'high': [102, 103, 104, 105],
            'low': [99, 100, 101, 102],
            'close': [101, 102, 103, 104],
            'volume': [1000, 2000, 3000, 4000],
        }, index=pd.date_range('2024-01-01', periods=4))
        
        validator = DataValidator('futures')
        report = validator.validate(df)
        
        assert not report.passed_all_checks
        price_issues = [i for i in report.issues if i.category == 'price']
        assert len(price_issues) > 0
    
    def test_validation_ohlc_logic(self):
        """Test OHLC logic validation."""
        df = pd.DataFrame({
            'open': [100, 101, 102, 103],
            'high': [95, 103, 104, 105],  # First high < open (invalid)
            'low': [99, 100, 101, 102],
            'close': [101, 102, 103, 104],
            'volume': [1000, 2000, 3000, 4000],
        }, index=pd.date_range('2024-01-01', periods=4))
        
        validator = DataValidator('futures')
        report = validator.validate(df)
        
        # Should detect OHLC violation
        ohlc_issues = [i for i in report.issues if i.category == 'ohlc']
        assert len(ohlc_issues) > 0
    
    def test_validation_summary_output(self):
        """Test that validation summary is human-readable."""
        df = pd.DataFrame({
            'close': [100, 101],
        }, index=pd.date_range('2024-01-01', periods=2))
        
        validator = DataValidator('futures')
        report = validator.validate(df)
        
        summary = report.summary()
        assert 'Data Quality Report' in summary
        assert 'records' in summary.lower()
    
    def test_validate_futures_data_convenience_function(self):
        """Test convenience function for futures validation."""
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [102, 103, 104],
            'low': [99, 100, 101],
            'close': [101, 102, 103],
            'volume': [1000, 2000, 3000],
        }, index=pd.date_range('2024-01-01', periods=3))
        
        report = validate_futures_data(df)
        assert isinstance(report, DataQualityReport)


class TestDataCleaning:
    """Test data cleaning functionality."""
    
    def test_cleaner_initialization(self):
        """Test DataCleaner initialization."""
        cleaner = DataCleaner('futures')
        assert cleaner.data_type == 'futures'
        assert cleaner.outlier_std == 5.0
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        df = pd.DataFrame({
            'close': [100, 101, 101, 102],
        }, index=pd.date_range('2024-01-01', periods=4))
        
        # Add exact duplicate
        df = pd.concat([df, df.iloc[[1]]])
        assert len(df) == 5
        
        cleaner = DataCleaner('futures')
        cleaned, log = cleaner.clean(df, handle_missing=False, remove_outliers=False)
        
        assert len(cleaned) < len(df)
        assert 'exact_duplicates_removed' in log
    
    def test_handle_missing_values(self):
        """Test missing value handling."""
        df = pd.DataFrame({
            'open': [100, np.nan, 102, 103],
            'high': [102, 103, 104, 105],
            'low': [99, 100, 101, 102],
            'close': [101, 102, 103, 104],
            'volume': [1000, 2000, 3000, 4000],
        }, index=pd.date_range('2024-01-01', periods=4))
        
        cleaner = DataCleaner('futures')
        cleaned, log = cleaner.clean(df, remove_duplicates=False, remove_outliers=False)
        
        # Should fill or remove the NaN
        assert cleaned['open'].notna().all()
    
    def test_fix_timestamps(self):
        """Test timestamp fixing."""
        df = pd.DataFrame({
            'close': [100, 101, 102],
        })
        
        # Add datetime column
        df['datetime'] = pd.date_range('2024-01-01', periods=3)
        
        cleaner = DataCleaner('futures')
        cleaned, log = cleaner.clean(df, remove_duplicates=False, handle_missing=False)
        
        # Should convert datetime column to index
        assert isinstance(cleaned.index, pd.DatetimeIndex)
        assert 'datetime_converted' in log or 'index_converted_to_datetime' in log
    
    def test_normalize_types(self):
        """Test data type normalization."""
        df = pd.DataFrame({
            'open': ['100', '101', '102'],
            'close': ['101', '102', '103'],
            'volume': ['1000', '2000', '3000'],
        }, index=pd.date_range('2024-01-01', periods=3))
        
        cleaner = DataCleaner('futures')
        cleaned, log = cleaner.clean(df)
        
        # Prices should be float
        assert cleaned['close'].dtype in [np.float64, np.float32]
        # Volume should be int
        assert cleaned['volume'].dtype == np.int64
    
    def test_clean_futures_data_convenience_function(self):
        """Test convenience function for cleaning."""
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [102, 103, 104],
            'low': [99, 100, 101],
            'close': [101, 102, 103],
            'volume': [1000, 2000, 3000],
        }, index=pd.date_range('2024-01-01', periods=3))
        
        cleaned, log = clean_futures_data(df)
        assert isinstance(cleaned, pd.DataFrame)
        assert isinstance(log, dict)
    
    def test_cleaning_summary(self):
        """Test cleaning summary output."""
        df = pd.DataFrame({
            'close': [100, 101],
        }, index=pd.date_range('2024-01-01', periods=2))
        
        cleaner = DataCleaner('futures')
        cleaned, log = cleaner.clean(df)
        
        summary = cleaner.get_cleaning_summary(log)
        assert 'Data Cleaning Summary' in summary


class TestParquetStorage:
    """Test Parquet storage functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ParquetStorage(tmpdir)
    
    @pytest.fixture
    def sample_futures_df(self):
        """Create sample futures DataFrame."""
        return pd.DataFrame({
            'open': [100.0, 101.0, 102.0],
            'high': [102.0, 103.0, 104.0],
            'low': [99.0, 100.0, 101.0],
            'close': [101.0, 102.0, 103.0],
            'volume': [1000, 2000, 3000],
            'open_interest': [50000, 51000, 52000],
        }, index=pd.date_range('2024-01-01', periods=3))
    
    def test_save_futures(self, temp_storage, sample_futures_df):
        """Test saving futures data."""
        path = temp_storage.save_futures(sample_futures_df, 'NIFTY')
        assert path.exists()
        assert 'nifty' in path.name
        assert 'futures' in path.name
    
    def test_load_futures(self, temp_storage, sample_futures_df):
        """Test loading futures data."""
        # Save first
        temp_storage.save_futures(sample_futures_df, 'NIFTY', overwrite=True)
        
        # Load
        loaded = temp_storage.load_futures('NIFTY')
        
        assert len(loaded) == len(sample_futures_df)
        assert list(loaded.columns) == list(sample_futures_df.columns)
        
        # Compare values (index freq may differ after save/load)
        pd.testing.assert_index_equal(loaded.index.normalize(), sample_futures_df.index.normalize())
        pd.testing.assert_frame_equal(loaded.reset_index(drop=True), sample_futures_df.reset_index(drop=True))
    
    def test_save_options(self, temp_storage):
        """Test saving options data."""
        df = pd.DataFrame({
            'strike': [19000, 19100, 19200],
            'call_price': [500, 400, 300],
            'put_price': [100, 200, 300],
        }, index=pd.date_range('2024-01-01', periods=3))
        
        path = temp_storage.save_options(df, 'NIFTY')
        assert path.exists()
        assert 'options' in path.name
    
    def test_load_options(self, temp_storage):
        """Test loading options data."""
        df = pd.DataFrame({
            'strike': [19000, 19100, 19200],
            'call_price': [500, 400, 300],
            'put_price': [100, 200, 300],
        }, index=pd.date_range('2024-01-01', periods=3))
        
        temp_storage.save_options(df, 'NIFTY', overwrite=True)
        loaded = temp_storage.load_options('NIFTY')
        
        assert len(loaded) == len(df)
        pd.testing.assert_frame_equal(loaded.reset_index(drop=True), df.reset_index(drop=True))
    
    def test_file_not_found_error(self, temp_storage):
        """Test that loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            temp_storage.load_futures('NONEXISTENT')
    
    def test_list_files(self, temp_storage, sample_futures_df):
        """Test listing files."""
        temp_storage.save_futures(sample_futures_df, 'NIFTY', overwrite=True)
        temp_storage.save_futures(sample_futures_df, 'BANKNIFTY', overwrite=True)
        
        files = temp_storage.list_files('futures')
        assert len(files) == 2
    
    def test_get_file_info(self, temp_storage, sample_futures_df):
        """Test getting file information."""
        path = temp_storage.save_futures(sample_futures_df, 'NIFTY')
        info = temp_storage.get_file_info(path)
        
        assert 'num_rows' in info
        assert 'num_columns' in info
        assert 'columns' in info
        assert info['num_rows'] == len(sample_futures_df)
    
    def test_convenience_functions(self, sample_futures_df):
        """Test convenience functions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save
            path = save_futures(sample_futures_df, 'NIFTY', tmpdir)
            assert path.exists()
            
            # Load
            loaded = load_futures('NIFTY', tmpdir)
            pd.testing.assert_frame_equal(loaded.reset_index(drop=True), sample_futures_df.reset_index(drop=True))


class TestSyntheticDataProvider:
    """Test synthetic data generation."""
    
    def test_synthetic_provider_initialization(self):
        """Test provider initialization."""
        provider = SyntheticDataProvider('NIFTY')
        assert provider.instrument == 'NIFTY'
    
    def test_generate_synthetic_futures_data(self):
        """Test generating synthetic futures data."""
        provider = SyntheticDataProvider('NIFTY', random_seed=42)
        df = provider.fetch_futures_data('2024-01-01', '2024-01-10')
        
        # Check DataFrame structure
        assert len(df) == 10  # 10 days
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns
        assert 'open_interest' in df.columns
    
    def test_synthetic_data_ohlc_logic(self):
        """Test that synthetic data follows OHLC logic."""
        provider = SyntheticDataProvider('NIFTY')
        df = provider.fetch_futures_data('2024-01-01', '2024-01-20')
        
        # Validate OHLC logic
        for idx in df.index:
            high = df.loc[idx, 'high']
            low = df.loc[idx, 'low']
            open_price = df.loc[idx, 'open']
            close = df.loc[idx, 'close']
            
            assert high >= open_price, f"High < Open at {idx}"
            assert high >= close, f"High < Close at {idx}"
            assert high >= low, f"High < Low at {idx}"
            assert low <= open_price, f"Low > Open at {idx}"
            assert low <= close, f"Low > Close at {idx}"
            assert low <= high, f"Low > High at {idx}"
    
    def test_synthetic_data_is_positive(self):
        """Test that synthetic prices are all positive."""
        provider = SyntheticDataProvider('NIFTY')
        df = provider.fetch_futures_data('2024-01-01', '2024-01-10')
        
        assert (df['open'] > 0).all()
        assert (df['high'] > 0).all()
        assert (df['low'] > 0).all()
        assert (df['close'] > 0).all()
        assert (df['volume'] > 0).all()
        assert (df['open_interest'] > 0).all()
    
    def test_synthetic_data_reproducibility(self):
        """Test that same seed produces same data."""
        provider1 = SyntheticDataProvider('NIFTY', random_seed=42)
        df1 = provider1.fetch_futures_data('2024-01-01', '2024-01-10')
        
        provider2 = SyntheticDataProvider('NIFTY', random_seed=42)
        df2 = provider2.fetch_futures_data('2024-01-01', '2024-01-10')
        
        pd.testing.assert_frame_equal(df1, df2)


class TestDataPipeline:
    """Integration tests for the full data pipeline."""
    
    def test_pipeline_synthetic_validation_cleaning_storage(self):
        """Test complete pipeline: generate -> validate -> clean -> store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Generate synthetic data
            provider = SyntheticDataProvider('NIFTY')
            raw_df = provider.fetch_futures_data('2024-01-01', '2024-01-20')
            
            # 2. Validate
            report = validate_futures_data(raw_df)
            assert report.passed_all_checks or len(report.issues) < 3  # Some minor issues OK
            
            # 3. Clean
            cleaned_df, log = clean_futures_data(raw_df)
            assert len(cleaned_df) > 0
            assert cleaned_df['close'].notna().all()
            
            # 4. Store
            storage = ParquetStorage(tmpdir)
            path = storage.save_futures(cleaned_df, 'NIFTY')
            
            # 5. Load and verify
            loaded_df = storage.load_futures('NIFTY')
            pd.testing.assert_frame_equal(loaded_df.reset_index(drop=True), cleaned_df.reset_index(drop=True))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
