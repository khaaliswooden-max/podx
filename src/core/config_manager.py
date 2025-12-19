"""
Configuration Manager
=====================

Centralized configuration management for PodX system.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class PodXConfig:
    """Main PodX configuration."""
    env: str = "development"
    log_level: str = "INFO"
    data_dir: str = "./data"
    config_dir: str = "./config"
    
    # XdoP settings
    xdop_compliance_level: str = "strict"
    xdop_certification_id: str = ""
    
    # Network settings
    ddil_cache_size_gb: int = 480000
    ddil_autonomy_hours: int = 24
    
    # Energy settings
    solar_array_kw: float = 15.0
    battery_capacity_kwh: float = 60.0
    
    # Thermal settings
    thermal_warning_threshold: float = 70.0
    thermal_critical_threshold: float = 85.0
    
    # Security settings
    crypto_algorithm: str = "AES-256-GCM"
    mfa_required: bool = True
    
    # Dashboard settings
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8080
    
    # Simulation mode
    simulation_mode: bool = True


class ConfigManager:
    """
    Manages PodX system configuration.
    
    Features:
    - Environment variable loading
    - Configuration file support
    - Runtime configuration updates
    - Configuration validation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.config = PodXConfig()
        
        self._load_environment()
        if config_path:
            self._load_config_file(config_path)
        
        logger.info(f"Configuration loaded: env={self.config.env}")
    
    def _load_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'PODX_ENV': ('env', str),
            'PODX_LOG_LEVEL': ('log_level', str),
            'PODX_DATA_DIR': ('data_dir', str),
            'PODX_CONFIG_DIR': ('config_dir', str),
            'XDOP_COMPLIANCE_LEVEL': ('xdop_compliance_level', str),
            'XDOP_CERTIFICATION_ID': ('xdop_certification_id', str),
            'DDIL_CACHE_SIZE_GB': ('ddil_cache_size_gb', int),
            'DDIL_AUTONOMY_HOURS': ('ddil_autonomy_hours', int),
            'SOLAR_ARRAY_KW': ('solar_array_kw', float),
            'BATTERY_CAPACITY_KWH': ('battery_capacity_kwh', float),
            'THERMAL_WARNING_THRESHOLD': ('thermal_warning_threshold', float),
            'THERMAL_CRITICAL_THRESHOLD': ('thermal_critical_threshold', float),
            'CRYPTO_ALGORITHM': ('crypto_algorithm', str),
            'AUTH_MFA_REQUIRED': ('mfa_required', lambda x: x.lower() == 'true'),
            'DASHBOARD_HOST': ('dashboard_host', str),
            'DASHBOARD_PORT': ('dashboard_port', int),
            'SIMULATION_MODE': ('simulation_mode', lambda x: x.lower() == 'true'),
        }
        
        for env_var, (attr, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    setattr(self.config, attr, converter(value))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}: {e}")
    
    def _load_config_file(self, path: str) -> None:
        """Load configuration from file."""
        config_path = Path(path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {path}")
            return
        
        try:
            with open(config_path) as f:
                data = json.load(f)
            
            for key, value in data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            logger.info(f"Loaded configuration from {path}")
            
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        save_path = Path(path or self.config_path or "./config/podx.json")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            key: getattr(self.config, key)
            for key in self.config.__dataclass_fields__
        }
        
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Configuration saved to {save_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            logger.info(f"Configuration updated: {key}={value}")
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            key: getattr(self.config, key)
            for key in self.config.__dataclass_fields__
        }
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return validation results."""
        issues = []
        warnings = []
        
        # Validate thermal thresholds
        if self.config.thermal_warning_threshold >= self.config.thermal_critical_threshold:
            issues.append("thermal_warning_threshold must be less than thermal_critical_threshold")
        
        # Validate XdoP compliance level
        valid_levels = ['strict', 'standard', 'minimal']
        if self.config.xdop_compliance_level not in valid_levels:
            issues.append(f"xdop_compliance_level must be one of: {valid_levels}")
        
        # Validate energy settings
        if self.config.solar_array_kw <= 0:
            issues.append("solar_array_kw must be positive")
        if self.config.battery_capacity_kwh <= 0:
            issues.append("battery_capacity_kwh must be positive")
        
        # Warnings
        if self.config.simulation_mode and self.config.env == 'production':
            warnings.append("simulation_mode is enabled in production environment")
        
        if not self.config.mfa_required and self.config.env == 'production':
            warnings.append("MFA is disabled in production environment")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
        }

