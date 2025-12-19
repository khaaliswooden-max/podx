"""
DDIL Network Controller
=======================

Core controller for Disconnected, Disrupted, Intermittent, and Limited (DDIL)
network operations, providing seamless connectivity across multiple network paths.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from threading import Thread, Event

logger = logging.getLogger(__name__)


class NetworkMode(Enum):
    """Available network connectivity modes."""
    SATELLITE = "satellite"      # Starlink Gen3
    CELLULAR_5G = "cellular_5g"  # 5G mmWave
    LORA_MESH = "lora_mesh"      # LoRa mesh network
    HF_RADIO = "hf_radio"        # HF radio backup
    WIRED = "wired"              # Ethernet (stationary)
    OFFLINE = "offline"          # Full DDIL mode


class ConnectionState(Enum):
    """State of a network connection."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    FAILING = "failing"


@dataclass
class NetworkPath:
    """Represents a single network path."""
    mode: NetworkMode
    state: ConnectionState = ConnectionState.DISCONNECTED
    latency_ms: float = 0
    bandwidth_mbps: float = 0
    packet_loss_pct: float = 0
    signal_strength_dbm: float = -100
    last_active: Optional[datetime] = None
    priority: int = 0
    enabled: bool = True


@dataclass
class DDILStatus:
    """Current DDIL operational status."""
    mode: str
    active_paths: List[str]
    primary_path: Optional[str]
    total_bandwidth_mbps: float
    average_latency_ms: float
    ddil_autonomy_remaining_hours: float
    cache_utilization_pct: float
    last_sync: Optional[datetime]
    next_sync_window: Optional[datetime]


class DDILController:
    """
    Main controller for DDIL network operations.
    
    Manages multiple network paths and provides seamless failover,
    predictive buffering, and autonomous operation capabilities.
    
    Attributes:
        paths: Dictionary of available network paths
        active_mode: Current primary network mode
        autonomy_hours: Configured DDIL autonomy duration
    """
    
    # Path priorities (lower = higher priority)
    DEFAULT_PRIORITIES = {
        NetworkMode.WIRED: 1,
        NetworkMode.CELLULAR_5G: 2,
        NetworkMode.SATELLITE: 3,
        NetworkMode.LORA_MESH: 4,
        NetworkMode.HF_RADIO: 5,
    }
    
    def __init__(
        self,
        autonomy_hours: float = 24,
        cache_size_tb: float = 480,
        handover_threshold_ms: float = 100
    ):
        """
        Initialize DDIL Controller.
        
        Args:
            autonomy_hours: Target DDIL autonomy duration
            cache_size_tb: Local cache capacity in TB
            handover_threshold_ms: Maximum acceptable handover latency
        """
        self.autonomy_hours = autonomy_hours
        self.cache_size_tb = cache_size_tb
        self.handover_threshold_ms = handover_threshold_ms
        
        self.paths: Dict[NetworkMode, NetworkPath] = {}
        self.active_mode: Optional[NetworkMode] = None
        self._running = False
        self._monitor_thread: Optional[Thread] = None
        self._stop_event = Event()
        
        self._callbacks: Dict[str, List[Callable]] = {
            'path_change': [],
            'handover': [],
            'ddil_enter': [],
            'ddil_exit': [],
        }
        
        self._initialize_paths()
        logger.info(f"DDIL Controller initialized: {autonomy_hours}hr autonomy, {cache_size_tb}TB cache")
    
    def _initialize_paths(self) -> None:
        """Initialize all network paths."""
        for mode in NetworkMode:
            if mode != NetworkMode.OFFLINE:
                self.paths[mode] = NetworkPath(
                    mode=mode,
                    priority=self.DEFAULT_PRIORITIES.get(mode, 10),
                )
    
    def start(self) -> None:
        """Start the DDIL controller and monitoring."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info("DDIL Controller started")
    
    def stop(self) -> None:
        """Stop the DDIL controller."""
        self._running = False
        self._stop_event.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        logger.info("DDIL Controller stopped")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running and not self._stop_event.is_set():
            try:
                self._update_path_status()
                self._check_handover_needed()
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
            
            self._stop_event.wait(timeout=1.0)
    
    def _update_path_status(self) -> None:
        """Update status of all network paths."""
        for mode, path in self.paths.items():
            if not path.enabled:
                continue
            
            # In simulation mode, generate realistic metrics
            self._simulate_path_metrics(path)
    
    def _simulate_path_metrics(self, path: NetworkPath) -> None:
        """Simulate realistic network metrics for testing."""
        import random
        
        if path.mode == NetworkMode.SATELLITE:
            path.latency_ms = 40 + random.uniform(-5, 15)
            path.bandwidth_mbps = 150 + random.uniform(-20, 50)
            path.signal_strength_dbm = -65 + random.uniform(-10, 10)
        elif path.mode == NetworkMode.CELLULAR_5G:
            path.latency_ms = 10 + random.uniform(-2, 5)
            path.bandwidth_mbps = 500 + random.uniform(-100, 200)
            path.signal_strength_dbm = -75 + random.uniform(-15, 15)
        elif path.mode == NetworkMode.LORA_MESH:
            path.latency_ms = 100 + random.uniform(-20, 50)
            path.bandwidth_mbps = 0.05 + random.uniform(-0.01, 0.02)
            path.signal_strength_dbm = -90 + random.uniform(-10, 10)
        elif path.mode == NetworkMode.HF_RADIO:
            path.latency_ms = 500 + random.uniform(-100, 200)
            path.bandwidth_mbps = 0.01 + random.uniform(-0.005, 0.005)
            path.signal_strength_dbm = -100 + random.uniform(-10, 10)
        elif path.mode == NetworkMode.WIRED:
            path.latency_ms = 1 + random.uniform(-0.5, 0.5)
            path.bandwidth_mbps = 10000
            path.signal_strength_dbm = 0
        
        path.packet_loss_pct = max(0, random.uniform(-0.5, 2))
        path.state = ConnectionState.CONNECTED if path.signal_strength_dbm > -95 else ConnectionState.DEGRADED
        path.last_active = datetime.now()
    
    def _check_handover_needed(self) -> None:
        """Check if network handover is needed."""
        if not self.active_mode:
            self._select_best_path()
            return
        
        current_path = self.paths.get(self.active_mode)
        if not current_path or current_path.state in [ConnectionState.DISCONNECTED, ConnectionState.FAILING]:
            self._select_best_path()
    
    def _select_best_path(self) -> None:
        """Select the best available network path."""
        available_paths = [
            (mode, path) for mode, path in self.paths.items()
            if path.enabled and path.state in [ConnectionState.CONNECTED, ConnectionState.DEGRADED]
        ]
        
        if not available_paths:
            if self.active_mode != NetworkMode.OFFLINE:
                self._enter_ddil_mode()
            return
        
        # Sort by priority, then by latency
        available_paths.sort(key=lambda x: (x[1].priority, x[1].latency_ms))
        best_mode, best_path = available_paths[0]
        
        if best_mode != self.active_mode:
            self._perform_handover(best_mode)
    
    def _perform_handover(self, new_mode: NetworkMode) -> None:
        """Perform network handover to new path."""
        old_mode = self.active_mode
        start_time = time.time()
        
        # Simulate handover process
        self.active_mode = new_mode
        
        handover_time_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Handover: {old_mode} -> {new_mode} ({handover_time_ms:.1f}ms)")
        
        for callback in self._callbacks['handover']:
            callback(old_mode, new_mode, handover_time_ms)
    
    def _enter_ddil_mode(self) -> None:
        """Enter full DDIL (offline) mode."""
        logger.warning("Entering DDIL mode - all network paths unavailable")
        self.active_mode = NetworkMode.OFFLINE
        
        for callback in self._callbacks['ddil_enter']:
            callback()
    
    def get_status(self) -> DDILStatus:
        """Get current DDIL operational status."""
        active_paths = [
            mode.value for mode, path in self.paths.items()
            if path.state == ConnectionState.CONNECTED
        ]
        
        total_bandwidth = sum(
            path.bandwidth_mbps for path in self.paths.values()
            if path.state == ConnectionState.CONNECTED
        )
        
        latencies = [
            path.latency_ms for path in self.paths.values()
            if path.state == ConnectionState.CONNECTED
        ]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        return DDILStatus(
            mode="connected" if self.active_mode != NetworkMode.OFFLINE else "ddil",
            active_paths=active_paths,
            primary_path=self.active_mode.value if self.active_mode else None,
            total_bandwidth_mbps=total_bandwidth,
            average_latency_ms=avg_latency,
            ddil_autonomy_remaining_hours=self.autonomy_hours,
            cache_utilization_pct=15.0,  # Simulated
            last_sync=datetime.now() - timedelta(minutes=5),
            next_sync_window=datetime.now() + timedelta(minutes=10),
        )
    
    def enable_path(self, mode: NetworkMode) -> None:
        """Enable a network path."""
        if mode in self.paths:
            self.paths[mode].enabled = True
            logger.info(f"Enabled path: {mode.value}")
    
    def disable_path(self, mode: NetworkMode) -> None:
        """Disable a network path."""
        if mode in self.paths:
            self.paths[mode].enabled = False
            if self.active_mode == mode:
                self._select_best_path()
            logger.info(f"Disabled path: {mode.value}")
    
    def force_handover(self, target_mode: NetworkMode) -> bool:
        """Force handover to specific network path."""
        if target_mode not in self.paths:
            return False
        
        path = self.paths[target_mode]
        if not path.enabled:
            return False
        
        self._perform_handover(target_mode)
        return True
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for network events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def get_path_metrics(self, mode: NetworkMode) -> Optional[Dict[str, Any]]:
        """Get detailed metrics for a specific path."""
        path = self.paths.get(mode)
        if not path:
            return None
        
        return {
            'mode': path.mode.value,
            'state': path.state.value,
            'latency_ms': path.latency_ms,
            'bandwidth_mbps': path.bandwidth_mbps,
            'packet_loss_pct': path.packet_loss_pct,
            'signal_strength_dbm': path.signal_strength_dbm,
            'last_active': path.last_active.isoformat() if path.last_active else None,
            'priority': path.priority,
            'enabled': path.enabled,
        }

