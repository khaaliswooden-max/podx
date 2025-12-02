import logging
from typing import Dict, List, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModuleState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    REMOVED = "removed"
    INSERTED = "inserted"

class HotSwapManager:
    """
    Manages hot-swappable modules, workload migration, and graceful degradation.
    """

    def __init__(self):
        self.modules = {}
        self.workloads = {} # module_id -> list of workloads

    def register_module(self, module_id: str, module_type: str):
        """Register a new module in the system."""
        self.modules[module_id] = {
            "type": module_type,
            "state": ModuleState.HEALTHY,
            "health_score": 100.0
        }
        self.workloads[module_id] = []
        logger.info(f"Module {module_id} ({module_type}) registered.")

    def update_health(self, module_id: str, health_score: float):
        """Update health score of a module."""
        if module_id in self.modules:
            self.modules[module_id]["health_score"] = health_score
            if health_score < 50:
                self.modules[module_id]["state"] = ModuleState.DEGRADED
                self._trigger_graceful_degradation(module_id)
            elif health_score == 0:
                self.modules[module_id]["state"] = ModuleState.FAILED
                self._evacuate_workloads(module_id)

    def handle_module_removal(self, module_id: str):
        """Handle physical removal of a module."""
        if module_id in self.modules:
            logger.warning(f"Module {module_id} removed!")
            self.modules[module_id]["state"] = ModuleState.REMOVED
            self._evacuate_workloads(module_id)

    def handle_module_insertion(self, module_id: str, module_type: str):
        """Handle physical insertion of a replacement module."""
        logger.info(f"Module {module_id} inserted.")
        self.register_module(module_id, module_type)
        self.modules[module_id]["state"] = ModuleState.INSERTED
        # Verify and activate
        self._verify_and_activate(module_id)

    def _verify_and_activate(self, module_id: str):
        """Verify module integrity and activate it."""
        # Simulation of hardware handshake and self-test
        logger.info(f"Verifying module {module_id}...")
        self.modules[module_id]["state"] = ModuleState.HEALTHY
        logger.info(f"Module {module_id} is now ACTIVE.")

    def _evacuate_workloads(self, module_id: str):
        """Migrate workloads from a failed/removed module to a healthy one."""
        if not self.workloads.get(module_id):
            return

        target_module = self._find_healthy_module(exclude=module_id)
        if target_module:
            logger.info(f"Migrating workloads from {module_id} to {target_module}...")
            # Move workloads
            self.workloads[target_module].extend(self.workloads[module_id])
            self.workloads[module_id] = []
            logger.info("Migration complete.")
        else:
            logger.critical(f"No healthy modules available to take over workloads from {module_id}!")

    def _trigger_graceful_degradation(self, module_id: str):
        """Reduce load on a degraded module."""
        logger.warning(f"Module {module_id} is degraded. Reducing load.")
        # Logic to shed non-critical tasks
        current_load = self.workloads[module_id]
        # Keep only critical tasks (simulated)
        self.workloads[module_id] = [w for w in current_load if w.get("priority") == "critical"]
        logger.info(f"Graceful degradation applied to {module_id}.")

    def _find_healthy_module(self, exclude: str) -> Optional[str]:
        """Find a healthy module to accept workloads."""
        for mid, data in self.modules.items():
            if mid != exclude and data["state"] == ModuleState.HEALTHY:
                return mid
        return None

    def assign_workload(self, module_id: str, workload: Dict):
        """Assign a workload to a module."""
        if module_id in self.workloads:
            self.workloads[module_id].append(workload)
