"""
Connectivity Manager
====================

Manages multi-path network connectivity including satellite, cellular,
mesh, and radio backup systems.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ConnectivityType(Enum):
    """Types of network connectivity."""
    STARLINK = "starlink"
    CELLULAR_5G = "cellular_5g"
    CELLULAR_LTE = "cellular_lte"
    LORA = "lora"
    HF_RADIO = "hf_radio"
    WIFI = "wifi"
    ETHERNET = "ethernet"


@dataclass
class ConnectionConfig:
    """Configuration for a network connection."""
    conn_type: ConnectivityType
    enabled: bool = True
    auto_connect: bool = True
    priority: int = 5
    bandwidth_limit_mbps: Optional[float] = None
    latency_target_ms: Optional[float] = None
    
    # Type-specific configuration
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class ConnectionStatus:
    """Current status of a network connection."""
    conn_type: ConnectivityType
    connected: bool
    signal_quality_pct: float
    latency_ms: float
    bandwidth_mbps: float
    uptime_seconds: float
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ConnectivityManager:
    """
    Manages all network connectivity options for PodX.
    
    Supports:
    - Starlink satellite (2× Gen3 terminals, 300 Mbps aggregate)
    - 5G mmWave cellular (4× modems with carrier aggregation)
    - LoRa mesh networking (10km radius)
    - HF radio backup
    - WiFi and Ethernet for local connectivity
    """
    
    def __init__(self):
        """Initialize connectivity manager."""
        self.connections: Dict[ConnectivityType, ConnectionConfig] = {}
        self.status_cache: Dict[ConnectivityType, ConnectionStatus] = {}
        self._initialize_default_connections()
        
        logger.info("Connectivity Manager initialized")
    
    def _initialize_default_connections(self) -> None:
        """Set up default connection configurations."""
        defaults = [
            ConnectionConfig(
                conn_type=ConnectivityType.STARLINK,
                priority=3,
                config={
                    'terminals': 2,
                    'aggregate_bandwidth_mbps': 300,
                    'dish_type': 'gen3',
                }
            ),
            ConnectionConfig(
                conn_type=ConnectivityType.CELLULAR_5G,
                priority=2,
                config={
                    'modems': 4,
                    'carrier_aggregation': True,
                    'bands': ['n77', 'n78', 'n79'],
                }
            ),
            ConnectionConfig(
                conn_type=ConnectivityType.LORA,
                priority=4,
                config={
                    'frequency_mhz': 915,
                    'spreading_factor': 7,
                    'bandwidth_khz': 125,
                    'range_km': 10,
                }
            ),
            ConnectionConfig(
                conn_type=ConnectivityType.HF_RADIO,
                priority=5,
                config={
                    'frequency_range_mhz': [3, 30],
                    'mode': 'ALE',
                    'power_watts': 100,
                }
            ),
            ConnectionConfig(
                conn_type=ConnectivityType.ETHERNET,
                priority=1,
                config={
                    'speed_gbps': 10,
                    'ports': 4,
                }
            ),
        ]
        
        for config in defaults:
            self.connections[config.conn_type] = config
    
    def get_connection_status(self, conn_type: ConnectivityType) -> ConnectionStatus:
        """
        Get current status of a connection.
        
        Args:
            conn_type: Type of connection to check
            
        Returns:
            ConnectionStatus with current metrics
        """
        # In simulation mode, generate realistic status
        return self._simulate_status(conn_type)
    
    def _simulate_status(self, conn_type: ConnectivityType) -> ConnectionStatus:
        """Generate simulated connection status."""
        import random
        
        if conn_type == ConnectivityType.STARLINK:
            return ConnectionStatus(
                conn_type=conn_type,
                connected=True,
                signal_quality_pct=85 + random.uniform(-5, 10),
                latency_ms=40 + random.uniform(-5, 15),
                bandwidth_mbps=280 + random.uniform(-30, 20),
                uptime_seconds=86400 + random.uniform(-3600, 3600),
                metadata={
                    'satellites_visible': 12 + random.randint(-2, 3),
                    'obstruction_pct': 2 + random.uniform(-1, 3),
                }
            )
        elif conn_type == ConnectivityType.CELLULAR_5G:
            return ConnectionStatus(
                conn_type=conn_type,
                connected=True,
                signal_quality_pct=75 + random.uniform(-10, 15),
                latency_ms=15 + random.uniform(-3, 10),
                bandwidth_mbps=800 + random.uniform(-200, 400),
                uptime_seconds=43200 + random.uniform(-3600, 3600),
                metadata={
                    'rsrp_dbm': -85 + random.uniform(-10, 10),
                    'rsrq_db': -10 + random.uniform(-3, 3),
                    'active_modems': 4,
                }
            )
        elif conn_type == ConnectivityType.LORA:
            return ConnectionStatus(
                conn_type=conn_type,
                connected=True,
                signal_quality_pct=70 + random.uniform(-15, 20),
                latency_ms=150 + random.uniform(-30, 50),
                bandwidth_mbps=0.05,
                uptime_seconds=172800,
                metadata={
                    'nodes_in_mesh': 5 + random.randint(-2, 3),
                    'rssi_dbm': -90 + random.uniform(-10, 10),
                }
            )
        elif conn_type == ConnectivityType.HF_RADIO:
            return ConnectionStatus(
                conn_type=conn_type,
                connected=True,
                signal_quality_pct=60 + random.uniform(-20, 25),
                latency_ms=500 + random.uniform(-100, 200),
                bandwidth_mbps=0.01,
                uptime_seconds=259200,
                metadata={
                    'frequency_mhz': 14.2,
                    'snr_db': 10 + random.uniform(-5, 5),
                }
            )
        else:
            return ConnectionStatus(
                conn_type=conn_type,
                connected=True,
                signal_quality_pct=100,
                latency_ms=1,
                bandwidth_mbps=10000,
                uptime_seconds=604800,
            )
    
    def get_all_status(self) -> Dict[ConnectivityType, ConnectionStatus]:
        """Get status of all configured connections."""
        return {
            conn_type: self.get_connection_status(conn_type)
            for conn_type in self.connections
        }
    
    def enable_connection(self, conn_type: ConnectivityType) -> bool:
        """Enable a connection type."""
        if conn_type in self.connections:
            self.connections[conn_type].enabled = True
            logger.info(f"Enabled connection: {conn_type.value}")
            return True
        return False
    
    def disable_connection(self, conn_type: ConnectivityType) -> bool:
        """Disable a connection type."""
        if conn_type in self.connections:
            self.connections[conn_type].enabled = False
            logger.info(f"Disabled connection: {conn_type.value}")
            return True
        return False
    
    def get_best_connection(self) -> Optional[ConnectivityType]:
        """Get the best available connection based on priority and status."""
        available = []
        
        for conn_type, config in self.connections.items():
            if not config.enabled:
                continue
            
            status = self.get_connection_status(conn_type)
            if status.connected and status.signal_quality_pct > 50:
                available.append((conn_type, config.priority, status))
        
        if not available:
            return None
        
        # Sort by priority (lower is better), then by signal quality
        available.sort(key=lambda x: (x[1], -x[2].signal_quality_pct))
        return available[0][0]
    
    def get_aggregate_bandwidth(self) -> float:
        """Get total available bandwidth across all connections."""
        total = 0.0
        
        for conn_type in self.connections:
            status = self.get_connection_status(conn_type)
            if status.connected:
                total += status.bandwidth_mbps
        
        return total
    
    def configure_connection(
        self,
        conn_type: ConnectivityType,
        **kwargs
    ) -> bool:
        """
        Update configuration for a connection.
        
        Args:
            conn_type: Connection type to configure
            **kwargs: Configuration parameters to update
            
        Returns:
            True if configuration was updated
        """
        if conn_type not in self.connections:
            return False
        
        config = self.connections[conn_type]
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                config.config[key] = value
        
        logger.info(f"Updated configuration for {conn_type.value}")
        return True


