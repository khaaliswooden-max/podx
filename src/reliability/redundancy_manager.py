from typing import List, Dict, Any
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComponentStatus(Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class RedundancyManager:
    """
    Manages hardware redundancy configurations to ensure high availability.
    Implements logic for:
    - N+1 compute modules
    - RAID-6 storage (survives 2-disk failures)
    - 4 independent WAN paths
    - N+2 battery banks
    - Dual redundant cooling systems
    """

    def __init__(self, compute_nodes: int = 4, storage_disks: int = 8):
        # N+1 Compute Configuration (e.g., if 3 needed, we have 4)
        self.compute_modules = self._initialize_compute(compute_nodes)
        
        # RAID-6 Storage (Minimum 4 disks, can survive 2 failures)
        self.storage_config = {
            "raid_level": "RAID-6",
            "total_disks": storage_disks,
            "min_disks_required": storage_disks - 2,
            "disks": [{"id": i, "status": ComponentStatus.ACTIVE} for i in range(storage_disks)]
        }
        
        # 4 Independent WAN Paths
        self.wan_paths = [
            {"id": "wan_1", "provider": "ISP_A", "status": ComponentStatus.ACTIVE},
            {"id": "wan_2", "provider": "ISP_B", "status": ComponentStatus.ACTIVE},
            {"id": "wan_3", "provider": "Satellite", "status": ComponentStatus.STANDBY},
            {"id": "wan_4", "provider": "5G_Backup", "status": ComponentStatus.STANDBY}
        ]
        
        # N+2 Battery Banks
        self.battery_banks = self._initialize_batteries(required=2, redundancy=2)
        
        # Dual Redundant Cooling
        self.cooling_systems = [
            {"id": "cooling_primary", "status": ComponentStatus.ACTIVE},
            {"id": "cooling_secondary", "status": ComponentStatus.STANDBY}
        ]

    def _initialize_compute(self, count: int) -> List[Dict[str, Any]]:
        """Initialize N+1 compute modules."""
        modules = []
        for i in range(count):
            modules.append({
                "id": f"compute_{i}",
                "status": ComponentStatus.ACTIVE if i < count - 1 else ComponentStatus.STANDBY,
                "role": "worker" if i < count - 1 else "spare"
            })
        return modules

    def _initialize_batteries(self, required: int, redundancy: int) -> List[Dict[str, Any]]:
        """Initialize N+2 battery banks."""
        total = required + redundancy
        banks = []
        for i in range(total):
            banks.append({
                "id": f"battery_{i}",
                "status": ComponentStatus.ACTIVE, # All active for load balancing usually, or some standby
                "capacity_percent": 100
            })
        return banks

    def check_compute_health(self) -> bool:
        """Verify N+1 compute redundancy."""
        active = sum(1 for m in self.compute_modules if m["status"] == ComponentStatus.ACTIVE)
        standby = sum(1 for m in self.compute_modules if m["status"] == ComponentStatus.STANDBY)
        # Assuming we need len - 1 active
        required = len(self.compute_modules) - 1
        is_healthy = active >= required or (active + standby) >= required
        logger.info(f"Compute Health: {'OK' if is_healthy else 'CRITICAL'} (Active: {active}, Standby: {standby})")
        return is_healthy

    def check_storage_health(self) -> bool:
        """Verify RAID-6 storage integrity (can survive 2 failures)."""
        active_disks = sum(1 for d in self.storage_config["disks"] if d["status"] == ComponentStatus.ACTIVE)
        is_healthy = active_disks >= self.storage_config["min_disks_required"]
        logger.info(f"Storage Health (RAID-6): {'OK' if is_healthy else 'CRITICAL'} (Active Disks: {active_disks}/{self.storage_config['total_disks']})")
        return is_healthy

    def check_wan_redundancy(self) -> bool:
        """Verify at least one WAN path is active."""
        active_paths = sum(1 for p in self.wan_paths if p["status"] == ComponentStatus.ACTIVE)
        is_healthy = active_paths >= 1
        logger.info(f"WAN Health: {'OK' if is_healthy else 'CRITICAL'} (Active Paths: {active_paths}/4)")
        return is_healthy

    def check_power_redundancy(self) -> bool:
        """Verify N+2 battery redundancy."""
        # Simplified check: ensure we haven't lost more than 2
        failed = sum(1 for b in self.battery_banks if b["status"] == ComponentStatus.FAILED)
        is_healthy = failed <= 2
        logger.info(f"Power Health: {'OK' if is_healthy else 'CRITICAL'} (Failed Banks: {failed})")
        return is_healthy

    def check_cooling_redundancy(self) -> bool:
        """Verify cooling redundancy."""
        operational = sum(1 for c in self.cooling_systems if c["status"] in [ComponentStatus.ACTIVE, ComponentStatus.STANDBY])
        is_healthy = operational >= 1
        logger.info(f"Cooling Health: {'OK' if is_healthy else 'CRITICAL'} (Operational: {operational}/2)")
        return is_healthy

    def get_system_status(self) -> Dict[str, bool]:
        return {
            "compute": self.check_compute_health(),
            "storage": self.check_storage_health(),
            "wan": self.check_wan_redundancy(),
            "power": self.check_power_redundancy(),
            "cooling": self.check_cooling_redundancy()
        }
