"""
Unit tests for configuration system.

Tests that configuration loading works correctly and all required
sections exist.
"""

import pytest
from pathlib import Path

from src.config import Config, get_config


class TestConfigLoading:
    """Test configuration loading."""
    
    def test_config_loads_successfully(self):
        """Test that config file loads without errors."""
        config = get_config()
        assert config is not None
        assert config.config is not None
    
    def test_config_paths_exist(self):
        """Test that config files exist at expected paths."""
        config = get_config()
        assert config.config_path.exists(), f"Config file not found: {config.config_path}"
        assert config.instruments_path.exists(), f"Instruments file not found: {config.instruments_path}"
    
    def test_project_config_sections(self):
        """Test that main config has expected sections."""
        config = get_config()
        expected_sections = [
            'project', 'data', 'backtesting', 'regimes',
            'strategies', 'volatility', 'classifier', 'logging'
        ]
        for section in expected_sections:
            assert section in config.config, f"Missing section: {section}"
    
    def test_instruments_config_sections(self):
        """Test that instruments config has expected sections."""
        config = get_config()
        assert 'instruments' in config.instruments
        assert 'NIFTY' in config.instruments['instruments']
    
    def test_get_with_dot_notation(self):
        """Test get() method with dot notation."""
        config = get_config()
        
        # Test valid paths
        initial_capital = config.get('backtesting.initial_capital')
        assert initial_capital is not None
        assert isinstance(initial_capital, (int, float))
        assert initial_capital > 0
        
        # Test nested path
        project_name = config.get('project.name')
        assert project_name == 'DerivaLens'
    
    def test_get_with_default(self):
        """Test get() method with default value."""
        config = get_config()
        
        # Non-existent key should return default
        result = config.get('nonexistent.key', 'default_value')
        assert result == 'default_value'
    
    def test_get_instrument(self):
        """Test get_instrument() method."""
        config = get_config()
        
        nifty_config = config.get_instrument('NIFTY')
        assert nifty_config is not None
        assert nifty_config['name'] == 'NIFTY 50'
        assert 'futures' in nifty_config
        assert 'options' in nifty_config
    
    def test_invalid_instrument_raises_error(self):
        """Test that requesting invalid instrument raises ValueError."""
        config = get_config()
        with pytest.raises(ValueError, match="not found"):
            config.get_instrument('INVALID_INSTRUMENT')
    
    def test_config_values_reasonable(self):
        """Test that key configuration values are reasonable."""
        config = get_config()
        
        # Initial capital should be positive
        assert config.get('backtesting.initial_capital') > 0
        
        # Risk-free rate should be between 0 and 1
        rfr = config.get('instruments.risk_free_rate')
        assert 0 <= rfr <= 0.2  # reasonable range
        
        # Position sizing
        max_position = config.get('backtesting.max_position_size_pct')
        assert 0 < max_position <= 100
    
    def test_config_singleton(self):
        """Test that get_config() returns same instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2


class TestInstrumentSpecifications:
    """Test instrument specifications."""
    
    def test_nifty_futures_specs(self):
        """Test NIFTY futures specifications."""
        config = get_config()
        nifty = config.get_instrument('NIFTY')
        
        futures_spec = nifty['futures']
        assert futures_spec['multiplier'] == 75
        assert futures_spec['tick_size'] > 0
        assert futures_spec['lot_size'] > 0
    
    def test_nifty_options_specs(self):
        """Test NIFTY options specifications."""
        config = get_config()
        nifty = config.get_instrument('NIFTY')
        
        options_spec = nifty['options']
        assert options_spec['multiplier'] == 100
        assert options_spec['tick_size'] > 0
        assert options_spec['style'] == 'European'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
