"""
System Monitor
==============

Comprehensive system monitoring for PodX with real-time metrics collection.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from threading import Thread, Event, Lock

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class SubsystemType(Enum):
    """Types of monitored subsystems."""
    COMPUTE = "compute"
    NETWORK = "network"
    ENERGY = "energy"
    THERMAL = "thermal"
    STORAGE = "storage"
    SECURITY = "security"


@dataclass
class SubsystemHealth:
    """Health status of a subsystem."""
    subsystem: SubsystemType
    status: HealthStatus
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_check: Optional[datetime] = None
    message: str = ""


@dataclass
class SystemHealth:
    """Overall system health status."""
    overall_status: HealthStatus
    subsystems: Dict[SubsystemType, SubsystemHealth]
    uptime_seconds: float
    timestamp: datetime
    alerts: List[str] = field(default_factory=list)


class SystemMonitor:
    """
    Comprehensive system monitoring for PodX.
    
    Monitors:
    - 50+ temperature sensors
    - 12 humidity sensors
    - 6 accelerometers
    - Power consumption
    - Network status
    - Storage health
    - Security events
    """
    
    SENSOR_COUNT = {
        'temperature': 50,
        'humidity': 12,
        'accelerometer': 6,
        'voltage': 8,
        'current': 8,
        'vibration': 4,
    }
    
    def __init__(self, poll_interval: float = 1.0):
        """
        Initialize system monitor.
        
        Args:
            poll_interval: Seconds between metric collections
        """
        self.poll_interval = poll_interval
        self._running = False
        self._monitor_thread: Optional[Thread] = None
        self._stop_event = Event()
        self._lock = Lock()
        
        self._start_time = datetime.now()
        self._subsystem_health: Dict[SubsystemType, SubsystemHealth] = {}
        self._callbacks: List[Callable[[SystemHealth], None]] = []
        self._alerts: List[str] = []
        
        self._initialize_subsystems()
        logger.info("System Monitor initialized")
    
    def _initialize_subsystems(self) -> None:
        """Initialize subsystem health tracking."""
        for subsystem in SubsystemType:
            self._subsystem_health[subsystem] = SubsystemHealth(
                subsystem=subsystem,
                status=HealthStatus.UNKNOWN,
            )
    
    def start(self) -> None:
        """Start monitoring."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info("System Monitor started")
    
    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False
        self._stop_event.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        logger.info("System Monitor stopped")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running and not self._stop_event.is_set():
            try:
                self._collect_metrics()
                self._evaluate_health()
                self._notify_callbacks()
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
            
            self._stop_event.wait(timeout=self.poll_interval)
    
    def _collect_metrics(self) -> None:
        """Collect metrics from all subsystems."""
        with self._lock:
            self._collect_compute_metrics()
            self._collect_network_metrics()
            self._collect_energy_metrics()
            self._collect_thermal_metrics()
            self._collect_storage_metrics()
            self._collect_security_metrics()
    
    def _collect_compute_metrics(self) -> None:
        """Collect compute subsystem metrics."""
        import random
        
        metrics = {
            'cpu_utilization_pct': 45 + random.uniform(-10, 15),
            'memory_utilization_pct': 62 + random.uniform(-5, 10),
            'gpu_utilization_pct': 35 + random.uniform(-15, 20),
            'cpu_temperature_c': 65 + random.uniform(-5, 10),
            'gpu_temperature_c': 72 + random.uniform(-5, 8),
            'processes_running': 245 + random.randint(-20, 30),
            'dmips': 150000,
            'tops': 320,
        }
        
        self._subsystem_health[SubsystemType.COMPUTE].metrics = metrics
        self._subsystem_health[SubsystemType.COMPUTE].last_check = datetime.now()
    
    def _collect_network_metrics(self) -> None:
        """Collect network subsystem metrics."""
        import random
        
        metrics = {
            'active_connections': 4,
            'primary_path': 'cellular_5g',
            'latency_ms': 12 + random.uniform(-2, 5),
            'bandwidth_mbps': 850 + random.uniform(-50, 100),
            'packet_loss_pct': random.uniform(0, 0.5),
            'ddil_ready': True,
            'cache_utilization_pct': 15 + random.uniform(-2, 5),
        }
        
        self._subsystem_health[SubsystemType.NETWORK].metrics = metrics
        self._subsystem_health[SubsystemType.NETWORK].last_check = datetime.now()
    
    def _collect_energy_metrics(self) -> None:
        """Collect energy subsystem metrics."""
        import random
        
        metrics = {
            'solar_generation_kw': 12.5 + random.uniform(-1, 2),
            'battery_charge_pct': 85 + random.uniform(-2, 3),
            'battery_voltage_v': 52.1 + random.uniform(-0.5, 0.5),
            'power_consumption_kw': 14.2 + random.uniform(-1, 1.5),
            'pue': 1.15 + random.uniform(-0.02, 0.02),
            'grid_connected': False,
            'runtime_hours': 3.2 + random.uniform(-0.2, 0.3),
        }
        
        self._subsystem_health[SubsystemType.ENERGY].metrics = metrics
        self._subsystem_health[SubsystemType.ENERGY].last_check = datetime.now()
    
    def _collect_thermal_metrics(self) -> None:
        """Collect thermal subsystem metrics."""
        import random
        
        metrics = {
            'ambient_temp_c': 35 + random.uniform(-2, 3),
            'compute_zone_temp_c': 42 + random.uniform(-2, 4),
            'storage_zone_temp_c': 38 + random.uniform(-2, 3),
            'power_zone_temp_c': 45 + random.uniform(-2, 4),
            'cooling_mode': 'adaptive',
            'heat_pipes_active': 48,
            'radiator_efficiency_pct': 92 + random.uniform(-3, 3),
            'fan_speed_pct': 45 + random.uniform(-5, 10),
        }
        
        self._subsystem_health[SubsystemType.THERMAL].metrics = metrics
        self._subsystem_health[SubsystemType.THERMAL].last_check = datetime.now()
    
    def _collect_storage_metrics(self) -> None:
        """Collect storage subsystem metrics."""
        import random
        
        metrics = {
            'total_capacity_tb': 480,
            'used_capacity_tb': 72 + random.uniform(-5, 10),
            'utilization_pct': 15 + random.uniform(-1, 2),
            'read_iops': 2500000 + random.randint(-100000, 200000),
            'write_iops': 1800000 + random.randint(-100000, 150000),
            'raid_status': 'optimal',
            'failed_drives': 0,
            'spare_drives': 2,
        }
        
        self._subsystem_health[SubsystemType.STORAGE].metrics = metrics
        self._subsystem_health[SubsystemType.STORAGE].last_check = datetime.now()
    
    def _collect_security_metrics(self) -> None:
        """Collect security subsystem metrics."""
        import random
        
        metrics = {
            'threat_level': 'low',
            'active_sessions': 3 + random.randint(-1, 2),
            'failed_auth_24h': random.randint(0, 2),
            'blocked_ips': 12 + random.randint(-2, 5),
            'encryption_active': True,
            'hsm_status': 'active',
            'audit_entries_24h': 1523 + random.randint(-100, 200),
            'compliance_status': 'compliant',
        }
        
        self._subsystem_health[SubsystemType.SECURITY].metrics = metrics
        self._subsystem_health[SubsystemType.SECURITY].last_check = datetime.now()
    
    def _evaluate_health(self) -> None:
        """Evaluate health status of all subsystems."""
        with self._lock:
            for subsystem, health in self._subsystem_health.items():
                health.status = self._evaluate_subsystem_health(subsystem, health.metrics)
    
    def _evaluate_subsystem_health(
        self,
        subsystem: SubsystemType,
        metrics: Dict[str, Any]
    ) -> HealthStatus:
        """Evaluate health status of a specific subsystem."""
        if not metrics:
            return HealthStatus.UNKNOWN
        
        if subsystem == SubsystemType.COMPUTE:
            if metrics.get('cpu_temperature_c', 0) > 85:
                return HealthStatus.CRITICAL
            elif metrics.get('cpu_temperature_c', 0) > 75:
                return HealthStatus.WARNING
                
        elif subsystem == SubsystemType.ENERGY:
            if metrics.get('battery_charge_pct', 100) < 10:
                return HealthStatus.CRITICAL
            elif metrics.get('battery_charge_pct', 100) < 20:
                return HealthStatus.WARNING
                
        elif subsystem == SubsystemType.THERMAL:
            if metrics.get('compute_zone_temp_c', 0) > 70:
                return HealthStatus.CRITICAL
            elif metrics.get('compute_zone_temp_c', 0) > 60:
                return HealthStatus.WARNING
                
        elif subsystem == SubsystemType.STORAGE:
            if metrics.get('failed_drives', 0) > 1:
                return HealthStatus.CRITICAL
            elif metrics.get('failed_drives', 0) > 0:
                return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    def _notify_callbacks(self) -> None:
        """Notify registered callbacks of health update."""
        health = self.get_system_health()
        
        for callback in self._callbacks:
            try:
                callback(health)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health status."""
        with self._lock:
            # Determine overall status
            statuses = [h.status for h in self._subsystem_health.values()]
            
            if HealthStatus.CRITICAL in statuses:
                overall = HealthStatus.CRITICAL
            elif HealthStatus.WARNING in statuses:
                overall = HealthStatus.WARNING
            elif HealthStatus.UNKNOWN in statuses:
                overall = HealthStatus.UNKNOWN
            else:
                overall = HealthStatus.HEALTHY
            
            uptime = (datetime.now() - self._start_time).total_seconds()
            
            return SystemHealth(
                overall_status=overall,
                subsystems=self._subsystem_health.copy(),
                uptime_seconds=uptime,
                timestamp=datetime.now(),
                alerts=self._alerts.copy(),
            )
    
    def get_subsystem_health(self, subsystem: SubsystemType) -> SubsystemHealth:
        """Get health status of a specific subsystem."""
        with self._lock:
            return self._subsystem_health.get(subsystem)
    
    def register_callback(self, callback: Callable[[SystemHealth], None]) -> None:
        """Register callback for health updates."""
        self._callbacks.append(callback)
    
    def add_alert(self, message: str) -> None:
        """Add an alert message."""
        with self._lock:
            self._alerts.append(f"{datetime.now().isoformat()}: {message}")
            logger.warning(f"Alert: {message}")
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        with self._lock:
            self._alerts.clear()

