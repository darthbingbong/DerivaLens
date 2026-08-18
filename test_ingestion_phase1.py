"""
Test data ingestion module structure.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing data ingestion module...")

# Test 1: Can we import?
try:
    # Just test imports (don't call methods that need pandas)
    from src.data.ingestion import DataProvider, DataIngestionError, get_data_provider
    print("✓ Successfully imported DataProvider, DataIngestionError, get_data_provider")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Can we instantiate abstract class?
try:
    from src.config import get_config
    provider = DataProvider('NIFTY')
    print(f"✓ Successfully instantiated DataProvider for NIFTY")
except Exception as e:
    print(f"✗ Failed to create provider: {e}")
    sys.exit(1)

# Test 3: Check that abstract methods exist
try:
    assert hasattr(provider, 'fetch_futures_data')
    assert hasattr(provider, 'fetch_options_data')
    assert hasattr(provider, 'fetch_spot_data')
    print("✓ All required methods exist on DataProvider")
except AssertionError as e:
    print(f"✗ Missing method: {e}")
    sys.exit(1)

# Test 4: Check factory function
try:
    config = get_config()
    # Just test that function exists and accepts parameters
    # Don't instantiate (pandas not installed yet)
    assert callable(get_data_provider)
    print("✓ get_data_provider factory function exists")
except Exception as e:
    print(f"✗ Factory function test failed: {e}")
    sys.exit(1)

print("\n✓ Data ingestion module structure validated (Phase 1)")
print("  Note: Full testing requires pandas (Phase 2)")
