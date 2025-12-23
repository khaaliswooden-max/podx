"""
System Orchestrator
===================

Central orchestration for all PodX subsystems.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from threading import Thread, Event

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """Overall system operational state."""
    INITIALIZING = "initializing"
    STARTING = "starting"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
    SHUTDOWN = "shutdown"


@dataclass
class SubsystemStatus:
    """Status of a managed subsystem."""
    name: str
    running: bool
    healthy: bool
    last_update: datetime
    error: Optional[str] = None


class SystemOrchestrator:
    """
    Central orchestrator for PodX system.
    
    Coordinates:
    - Subsystem lifecycle management
    - Inter-subsystem communication
    - System state management
    - Emergency procedures
    """
    
    def __init__(self):
        """Initialize system orchestrator."""
        self.state = SystemState.INITIALIZING
        self._subsystems: Dict[str, Any] = {}
        self._subsystem_status: Dict[str, SubsystemStatus] = {}
        self._running = False
        self._orchestrator_thread: Optional[Thread] = None
        self._stop_event = Event()
        
        logger.info("System Orchestrator initialized")
    
    def register_subsystem(self, name: str, subsystem: Any) -> None:
        """Register a subsystem for orchestration."""
        self._subsystems[name] = subsystem
        self._subsystem_status[name] = SubsystemStatus(
            name=name,
            running=False,
            healthy=False,
            last_update=datetime.now(),
        )
        logger.info(f"Registered subsystem: {name}")
    
    def start(self) -> bool:
        """Start the system and all subsystems."""
        logger.info("Starting PodX system...")
        self.state = SystemState.STARTING
        
        try:
            # Start all subsystems
            for name, subsystem in self._subsystems.items():
                logger.info(f"Starting subsystem: {name}")
                if hasattr(subsystem, 'start'):
                    subsystem.start()
                self._subsystem_status[name].running = True
                self._subsystem_status[name].healthy = True
                self._subsystem_status[name].last_update = datetime.now()
            
            # Start orchestration loop
            self._running = True
            self._stop_event.clear()
            self._orchestrator_thread = Thread(target=self._orchestration_loop, daemon=True)
            self._orchestrator_thread.start()
            
            self.state = SystemState.OPERATIONAL
            logger.info("PodX system started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            self.state = SystemState.DEGRADED
            return False
    
    def stop(self) -> None:
        """Stop the system and all subsystems."""
        logger.info("Stopping PodX system...")
        self.state = SystemState.SHUTDOWN
        
        self._running = False
        self._stop_event.set()
        
        if self._orchestrator_thread:
            self._orchestrator_thread.join(timeout=5)
        
        # Stop all subsystems
        for name, subsystem in self._subsystems.items():
            logger.info(f"Stopping subsystem: {name}")
            if hasattr(subsystem, 'stop'):
                try:
                    subsystem.stop()
                except Exception as e:
                    logger.error(f"Error stopping {name}: {e}")
            self._subsystem_status[name].running = False
        
        logger.info("PodX system stopped")
    
    def _orchestration_loop(self) -> None:
        """Main orchestration loop."""
        while self._running and not self._stop_event.is_set():
            try:
                self._check_subsystem_health()
                self._update_system_state()
            except Exception as e:
                logger.error(f"Orchestration loop error: {e}")
            
            self._stop_event.wait(timeout=1.0)
    
    def _check_subsystem_health(self) -> None:
        """Check health of all subsystems."""
        for name, subsystem in self._subsystems.items():
            try:
                if hasattr(subsystem, 'get_health'):
                    health = subsystem.get_health()
                    self._subsystem_status[name].healthy = health.get('healthy', True)
                else:
                    self._subsystem_status[name].healthy = True
                
                self._subsystem_status[name].last_update = datetime.now()
                self._subsystem_status[name].error = None
                
            except Exception as e:
                self._subsystem_status[name].healthy = False
                self._subsystem_status[name].error = str(e)
                logger.warning(f"Subsystem {name} health check failed: {e}")
    
    def _update_system_state(self) -> None:
        """Update overall system state based on subsystem health."""
        if self.state == SystemState.SHUTDOWN:
            return
        
        unhealthy = [
            name for name, status in self._subsystem_status.items()
            if not status.healthy
        ]
        
        if len(unhealthy) == 0:
            self.state = SystemState.OPERATIONAL
        elif len(unhealthy) < len(self._subsystems) / 2:
            self.state = SystemState.DEGRADED
            logger.warning(f"System degraded: unhealthy subsystems: {unhealthy}")
        else:
            self.state = SystemState.EMERGENCY
            logger.error(f"System emergency: many unhealthy subsystems: {unhealthy}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            'state': self.state.value,
            'subsystems': {
                name: {
                    'running': status.running,
                    'healthy': status.healthy,
                    'last_update': status.last_update.isoformat(),
                    'error': status.error,
                }
                for name, status in self._subsystem_status.items()
            },
            'timestamp': datetime.now().isoformat(),
        }
    
    def enter_maintenance_mode(self) -> None:
        """Enter maintenance mode."""
        logger.info("Entering maintenance mode")
        self.state = SystemState.MAINTENANCE
    
    def exit_maintenance_mode(self) -> None:
        """Exit maintenance mode."""
        logger.info("Exiting maintenance mode")
        self._update_system_state()
    
    def trigger_emergency_shutdown(self, reason: str) -> None:
        """Trigger emergency shutdown procedure."""
        logger.critical(f"EMERGENCY SHUTDOWN: {reason}")
        self.state = SystemState.EMERGENCY
        self.stop()


