"""
Phase 2 Quick Start Examples

This script demonstrates the complete data pipeline:
1. Generate synthetic data
2. Validate data quality
3. Clean the data
4. Store to Parquet
5. Load and verify
"""

from src.config import get_config
from src.data.ingestion import SyntheticDataProvider
from src.data.validation import validate_futures_data
from src.data.cleaning import clean_futures_data
from src.data.storage import ParquetStorage


def example_1_generate_and_validate():
    """Example 1: Generate synthetic data and validate it."""
    print("\n" + "=" * 70)
    print("Example 1: Generate and Validate Synthetic Data")
    print("=" * 70)
    
    # Generate synthetic NIFTY futures data
    provider = SyntheticDataProvider('NIFTY', random_seed=42)
    raw_data = provider.fetch_futures_data('2024-01-01', '2024-01-10')
    
    print(f"\nGenerated {len(raw_data)} days of synthetic data")
    print(f"Price range: {raw_data['close'].min():.2f} - {raw_data['close'].max():.2f}")
    print(f"Volume range: {raw_data['volume'].min():,} - {raw_data['volume'].max():,}")
    
    # Validate the data
    report = validate_futures_data(raw_data)
    print("\n" + report.summary())
    
    return raw_data


def example_2_clean_data(raw_data):
    """Example 2: Clean the data."""
    print("\n" + "=" * 70)
    print("Example 2: Clean the Data")
    print("=" * 70)
    
    cleaned_data, log = clean_futures_data(raw_data)
    
    print(f"\nStarting with {len(raw_data)} records")
    print(f"After cleaning: {len(cleaned_data)} records")
    
    print("\nCleaning operations performed:")
    for operation, count in sorted(log.items()):
        if count > 0:
            print(f"  • {operation}: {count}")
    
    # Verify data quality after cleaning
    report = validate_futures_data(cleaned_data)
    if report.passed_all_checks:
        print("\n✓ Data quality is excellent!")
    else:
        print(f"\n⚠ Found {len(report.issues)} minor issue(s)")
    
    return cleaned_data


def example_3_store_and_load(cleaned_data):
    """Example 3: Store to Parquet and load back."""
    print("\n" + "=" * 70)
    print("Example 3: Store to Parquet and Load")
    print("=" * 70)
    
    # Store the data
    storage = ParquetStorage()
    filepath = storage.save_futures(cleaned_data, 'NIFTY')
    print(f"\n✓ Saved to: {filepath}")
    
    # Get file info
    info = storage.get_file_info(filepath)
    print(f"\nFile Info:")
    print(f"  • Size: {info['size_mb']:.2f} MB")
    print(f"  • Rows: {info['num_rows']:,}")
    print(f"  • Columns: {info['num_columns']}")
    print(f"  • Columns: {', '.join(info['columns'])}")
    
    # Load it back
    loaded_data = storage.load_futures('NIFTY')
    print(f"\n✓ Loaded {len(loaded_data)} records")
    
    return loaded_data


def example_4_complete_pipeline():
    """Example 4: Complete pipeline in one go."""
    print("\n" + "=" * 70)
    print("Example 4: Complete Data Pipeline")
    print("=" * 70)
    
    config = get_config()
    
    # Step 1: Generate
    print("\n1. Generating synthetic data...")
    provider = SyntheticDataProvider('NIFTY', random_seed=42)
    data = provider.fetch_futures_data('2024-01-01', '2024-02-29')
    print(f"   Generated {len(data)} trading days")
    
    # Step 2: Validate (before)
    print("\n2. Validating raw data...")
    report_before = validate_futures_data(data)
    print(f"   Found {len(report_before.issues)} issue(s)")
    
    # Step 3: Clean
    print("\n3. Cleaning data...")
    cleaned, log = clean_futures_data(data)
    print(f"   {len(data) - len(cleaned)} records removed during cleaning")
    
    # Step 4: Validate (after)
    print("\n4. Validating cleaned data...")
    report_after = validate_futures_data(cleaned)
    if report_after.passed_all_checks:
        print("   ✓ All checks passed!")
    else:
        print(f"   {len(report_after.issues)} issue(s) remaining")
    
    # Step 5: Store
    print("\n5. Storing to Parquet...")
    storage = ParquetStorage()
    storage.save_futures(cleaned, 'NIFTY', overwrite=True)
    print("   ✓ Saved successfully")
    
    # Step 6: Verify
    print("\n6. Verifying loaded data...")
    loaded = storage.load_futures('NIFTY')
    print(f"   ✓ Loaded {len(loaded)} records")
    print(f"   First date: {loaded.index[0].date()}")
    print(f"   Last date: {loaded.index[-1].date()}")
    print(f"   Close price range: {loaded['close'].min():.2f} - {loaded['close'].max():.2f}")
    
    print("\n" + "=" * 70)
    print("✓ Complete pipeline executed successfully!")
    print("=" * 70)


def example_5_storage_operations():
    """Example 5: Various storage operations."""
    print("\n" + "=" * 70)
    print("Example 5: Storage Operations")
    print("=" * 70)
    
    storage = ParquetStorage()
    
    # Generate test data for multiple instruments
    print("\nGenerating test data for multiple instruments...")
    for instrument in ['NIFTY', 'BANKNIFTY', 'FINNIFTY']:
        provider = SyntheticDataProvider(instrument)
        data = provider.fetch_futures_data('2024-01-01', '2024-01-20')
        storage.save_futures(data, instrument, overwrite=True)
        print(f"  ✓ Saved {instrument}: {len(data)} records")
    
    # List all files
    print("\nAll stored futures files:")
    files = storage.list_files('futures')
    for f in files:
        print(f"  • {f.name}")
    
    print(f"\nTotal files: {len(files)}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  DerivaLens Phase 2: Data Pipeline Examples".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Run examples
        raw_data = example_1_generate_and_validate()
        cleaned_data = example_2_clean_data(raw_data)
        example_3_store_and_load(cleaned_data)
        example_4_complete_pipeline()
        example_5_storage_operations()
        
        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
