#!/usr/bin/env python
"""Quick validation of Phase 1 setup."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("DerivaLens Phase 1 Validation")
print("=" * 60)

# Test 1: Import configuration
print("\n[1/5] Testing configuration import...")
try:
    from src.config import get_config
    print("  ✓ Configuration module imported successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 2: Load configuration
print("\n[2/5] Testing configuration loading...")
try:
    config = get_config()
    print("  ✓ Configuration loaded successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 3: Verify project settings
print("\n[3/5] Testing project configuration...")
try:
    name = config.get('project.name')
    version = config.get('project.version')
    assert name == 'DerivaLens', f"Expected name 'DerivaLens', got '{name}'"
    print(f"  ✓ Project: {name} v{version}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 4: Verify backtesting config
print("\n[4/5] Testing backtesting configuration...")
try:
    initial_capital = config.get('backtesting.initial_capital')
    slippage = config.get('backtesting.slippage_bps')
    assert initial_capital > 0, "Initial capital should be positive"
    assert 0 < slippage < 10, "Slippage should be reasonable"
    print(f"  ✓ Initial capital: Rs {initial_capital:,.0f}")
    print(f"  ✓ Slippage: {slippage} bps")
    print(f"  ✓ Risk per trade: {config.get('backtesting.risk_per_trade_pct')}%")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 5: Verify instrument configuration
print("\n[5/5] Testing instrument configuration...")
try:
    nifty = config.get_instrument('NIFTY')
    print(f"  ✓ Instrument: {nifty['name']}")
    print(f"  ✓ Futures multiplier: {nifty['futures']['multiplier']}")
    print(f"  ✓ Options multiplier: {nifty['options']['multiplier']}")
    print(f"  ✓ Exchange: {nifty['exchange']}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL PHASE 1 CHECKS PASSED")
print("=" * 60)
print("\nNext steps:")
print("1. Review the DEVELOPMENT.md for Phase 2 details")
print("2. Run: pytest tests/test_config.py -v")
print("3. Start Phase 2: Data Ingestion & Validation")
print("=" * 60)
