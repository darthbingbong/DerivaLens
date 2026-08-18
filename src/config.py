"""
Configuration management for DerivaLens.

Loads and manages configuration from YAML files and environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration manager for DerivaLens."""
    
    def __init__(self, config_path: str | Path | None = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config.yaml file. If None, uses default.
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Locate config relative to this file: src/config.py
            # Go up 2 levels: src/ -> DerivaLens/
            project_root = Path(__file__).parent.parent
            self.config_path = project_root / "config" / "config.yaml"
        
        self.instruments_path = self.config_path.parent / "instruments.yaml"
        
        # Load configuration files
        self._load_configs()
        
        # Override with environment variables where applicable
        self._load_env_overrides()
    
    def _load_configs(self) -> None:
        """Load YAML configuration files."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        if not self.instruments_path.exists():
            raise FileNotFoundError(f"Instruments file not found: {self.instruments_path}")
        
        with open(self.instruments_path, 'r') as f:
            self.instruments = yaml.safe_load(f)
        
        logger.info(f"Loaded config from {self.config_path}")
        logger.info(f"Loaded instruments from {self.instruments_path}")
    
    def _load_env_overrides(self) -> None:
        """Override config with environment variables."""
        # Log level
        if log_level := os.getenv('LOG_LEVEL'):
            self.config['logging']['level'] = log_level
        
        # Risk-free rate
        if rfr := os.getenv('RISK_FREE_RATE'):
            self.config['instruments']['risk_free_rate'] = float(rfr)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Example:
            config.get('backtesting.initial_capital')
            config.get('instruments.futures.tick_size')
        
        Args:
            key: Configuration key (dot-separated path).
            default: Default value if key not found.
        
        Returns:
            Configuration value.
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_instrument(self, name: str) -> Dict[str, Any]:
        """
        Get instrument configuration.
        
        Args:
            name: Instrument name (e.g., 'NIFTY').
        
        Returns:
            Instrument configuration dictionary.
        
        Raises:
            ValueError: If instrument not found.
        """
        if name not in self.instruments.get('instruments', {}):
            raise ValueError(f"Instrument '{name}' not found in configuration")
        
        return self.instruments['instruments'][name]
    
    def __repr__(self) -> str:
        return f"Config(path={self.config_path})"


# Global configuration instance
_config_instance: Config | None = None


def get_config() -> Config:
    """Get or create global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


# Example usage
if __name__ == "__main__":
    config = get_config()
    print(f"Initial capital: {config.get('backtesting.initial_capital')}")
    print(f"Risk-free rate: {config.get('instruments.risk_free_rate')}")
    print(f"NIFTY config: {config.get_instrument('NIFTY')}")
