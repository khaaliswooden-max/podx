"""
Storage Manager
===============

Manages 480TB NVMe storage array with RAID-6 protection.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class DriveStatus(Enum):
    """Status of individual storage drives."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    REBUILDING = "rebuilding"
    SPARE = "spare"


@dataclass
class StorageDrive:
    """Represents a storage drive."""
    id: str
    capacity_tb: float
    status: DriveStatus
    temperature_c: float
    health_pct: float
    power_on_hours: int
    read_errors: int
    write_errors: int


@dataclass
class StorageStats:
    """Storage system statistics."""
    total_capacity_tb: float
    used_capacity_tb: float
    free_capacity_tb: float
    utilization_pct: float
    read_iops: int
    write_iops: int
    read_throughput_gbps: float
    write_throughput_gbps: float
    raid_status: str
    drives_healthy: int
    drives_total: int


class StorageManager:
    """
    Manages PodX storage subsystem.
    
    Features:
    - 480TB total capacity
    - RAID-6 protection (survives 2 drive failures)
    - 28 GB/s sequential read
    - 24 GB/s sequential write
    - 8M random IOPS
    """
    
    TOTAL_CAPACITY_TB = 480
    DRIVE_COUNT = 24
    DRIVE_CAPACITY_TB = 24  # Per drive
    SPARE_DRIVES = 2
    
    def __init__(self):
        """Initialize storage manager."""
        self._drives: Dict[str, StorageDrive] = {}
        self._used_tb = 0.0
        self._initialize_drives()
        
        logger.info(f"Storage Manager initialized: {self.TOTAL_CAPACITY_TB}TB capacity")
    
    def _initialize_drives(self) -> None:
        """Initialize storage drives."""
        import random
        
        for i in range(self.DRIVE_COUNT):
            drive_id = f"NVMe-{i:02d}"
            
            # Last 2 drives are spares
            is_spare = i >= (self.DRIVE_COUNT - self.SPARE_DRIVES)
            
            self._drives[drive_id] = StorageDrive(
                id=drive_id,
                capacity_tb=self.DRIVE_CAPACITY_TB,
                status=DriveStatus.SPARE if is_spare else DriveStatus.HEALTHY,
                temperature_c=35 + random.uniform(-3, 5),
                health_pct=100 - random.uniform(0, 2),
                power_on_hours=random.randint(100, 5000),
                read_errors=0,
                write_errors=0,
            )
    
    def get_stats(self) -> StorageStats:
        """Get current storage statistics."""
        import random
        
        healthy_drives = sum(
            1 for d in self._drives.values()
            if d.status in [DriveStatus.HEALTHY, DriveStatus.SPARE]
        )
        
        # Simulate usage
        used = 72 + random.uniform(-5, 10)
        
        return StorageStats(
            total_capacity_tb=self.TOTAL_CAPACITY_TB,
            used_capacity_tb=used,
            free_capacity_tb=self.TOTAL_CAPACITY_TB - used,
            utilization_pct=(used / self.TOTAL_CAPACITY_TB) * 100,
            read_iops=2500000 + random.randint(-100000, 200000),
            write_iops=1800000 + random.randint(-100000, 150000),
            read_throughput_gbps=28 + random.uniform(-2, 1),
            write_throughput_gbps=24 + random.uniform(-2, 1),
            raid_status="optimal",
            drives_healthy=healthy_drives,
            drives_total=self.DRIVE_COUNT,
        )
    
    def get_drive_status(self, drive_id: str) -> Optional[StorageDrive]:
        """Get status of a specific drive."""
        return self._drives.get(drive_id)
    
    def get_all_drives(self) -> List[StorageDrive]:
        """Get status of all drives."""
        return list(self._drives.values())
    
    def check_raid_health(self) -> Dict[str, Any]:
        """Check RAID array health."""
        failed = [d for d in self._drives.values() if d.status == DriveStatus.FAILED]
        degraded = [d for d in self._drives.values() if d.status == DriveStatus.DEGRADED]
        rebuilding = [d for d in self._drives.values() if d.status == DriveStatus.REBUILDING]
        
        if len(failed) >= 3:
            status = "critical"
        elif len(failed) >= 1 or len(degraded) >= 2:
            status = "degraded"
        elif len(rebuilding) > 0:
            status = "rebuilding"
        else:
            status = "optimal"
        
        return {
            'status': status,
            'failed_drives': len(failed),
            'degraded_drives': len(degraded),
            'rebuilding_drives': len(rebuilding),
            'can_survive_failure': len(failed) < 2,
            'spare_drives_available': sum(
                1 for d in self._drives.values() if d.status == DriveStatus.SPARE
            ),
        }
    
    def simulate_drive_failure(self, drive_id: str) -> bool:
        """Simulate a drive failure for testing."""
        if drive_id not in self._drives:
            return False
        
        drive = self._drives[drive_id]
        drive.status = DriveStatus.FAILED
        
        # Find a spare and start rebuild
        for spare_id, spare in self._drives.items():
            if spare.status == DriveStatus.SPARE:
                spare.status = DriveStatus.REBUILDING
                logger.warning(f"Drive {drive_id} failed, rebuilding on {spare_id}")
                break
        
        return True
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        stats = self.get_stats()
        raid = self.check_raid_health()
        
        drives_by_status = {}
        for status in DriveStatus:
            drives_by_status[status.value] = sum(
                1 for d in self._drives.values() if d.status == status
            )
        
        avg_temp = sum(d.temperature_c for d in self._drives.values()) / len(self._drives)
        avg_health = sum(d.health_pct for d in self._drives.values()) / len(self._drives)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': raid['status'],
            'capacity': {
                'total_tb': stats.total_capacity_tb,
                'used_tb': stats.used_capacity_tb,
                'free_tb': stats.free_capacity_tb,
                'utilization_pct': stats.utilization_pct,
            },
            'performance': {
                'read_iops': stats.read_iops,
                'write_iops': stats.write_iops,
                'read_throughput_gbps': stats.read_throughput_gbps,
                'write_throughput_gbps': stats.write_throughput_gbps,
            },
            'raid': raid,
            'drives': drives_by_status,
            'health': {
                'average_temperature_c': avg_temp,
                'average_health_pct': avg_health,
            },
        }

