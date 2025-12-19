"""
RAID Controller
===============

RAID-6 array management for data protection.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RAIDLevel(Enum):
    """Supported RAID levels."""
    RAID_0 = "RAID-0"
    RAID_1 = "RAID-1"
    RAID_5 = "RAID-5"
    RAID_6 = "RAID-6"
    RAID_10 = "RAID-10"


class ArrayStatus(Enum):
    """RAID array status."""
    OPTIMAL = "optimal"
    DEGRADED = "degraded"
    REBUILDING = "rebuilding"
    FAILED = "failed"
    OFFLINE = "offline"


@dataclass
class RAIDArray:
    """Represents a RAID array."""
    id: str
    level: RAIDLevel
    status: ArrayStatus
    capacity_tb: float
    usable_capacity_tb: float
    stripe_size_kb: int
    drives: List[str]
    spare_drives: List[str]
    rebuild_progress_pct: Optional[float] = None


class RAIDController:
    """
    RAID-6 array controller.
    
    Features:
    - Dual parity for 2-drive failure tolerance
    - Hot spare management
    - Automatic rebuild
    - Scrubbing and verification
    """
    
    def __init__(self):
        """Initialize RAID controller."""
        self._arrays: Dict[str, RAIDArray] = {}
        self._initialize_default_array()
        
        logger.info("RAID Controller initialized")
    
    def _initialize_default_array(self) -> None:
        """Initialize the default RAID-6 array."""
        self._arrays['primary'] = RAIDArray(
            id='primary',
            level=RAIDLevel.RAID_6,
            status=ArrayStatus.OPTIMAL,
            capacity_tb=480,
            usable_capacity_tb=432,  # RAID-6 overhead
            stripe_size_kb=256,
            drives=[f"NVMe-{i:02d}" for i in range(22)],
            spare_drives=["NVMe-22", "NVMe-23"],
        )
    
    def get_array_status(self, array_id: str = 'primary') -> Optional[RAIDArray]:
        """Get status of a RAID array."""
        return self._arrays.get(array_id)
    
    def get_all_arrays(self) -> List[RAIDArray]:
        """Get all RAID arrays."""
        return list(self._arrays.values())
    
    def check_redundancy(self, array_id: str = 'primary') -> Dict:
        """Check redundancy status of an array."""
        array = self._arrays.get(array_id)
        if not array:
            return {'error': 'Array not found'}
        
        return {
            'array_id': array_id,
            'level': array.level.value,
            'status': array.status.value,
            'fault_tolerance': 2 if array.level == RAIDLevel.RAID_6 else 1,
            'can_lose_drives': 2 if array.status == ArrayStatus.OPTIMAL else 1,
            'spare_drives_available': len(array.spare_drives),
            'is_protected': array.status in [ArrayStatus.OPTIMAL, ArrayStatus.REBUILDING],
        }
    
    def start_rebuild(self, array_id: str, failed_drive: str, spare_drive: str) -> bool:
        """Start array rebuild using a spare drive."""
        array = self._arrays.get(array_id)
        if not array:
            return False
        
        if spare_drive not in array.spare_drives:
            logger.error(f"Drive {spare_drive} is not a spare")
            return False
        
        # Remove failed drive and add spare
        if failed_drive in array.drives:
            array.drives.remove(failed_drive)
        
        array.spare_drives.remove(spare_drive)
        array.drives.append(spare_drive)
        
        array.status = ArrayStatus.REBUILDING
        array.rebuild_progress_pct = 0.0
        
        logger.info(f"Started rebuild: {failed_drive} -> {spare_drive}")
        return True
    
    def get_rebuild_status(self, array_id: str = 'primary') -> Optional[Dict]:
        """Get rebuild progress."""
        array = self._arrays.get(array_id)
        if not array:
            return None
        
        if array.status != ArrayStatus.REBUILDING:
            return {
                'rebuilding': False,
                'status': array.status.value,
            }
        
        return {
            'rebuilding': True,
            'progress_pct': array.rebuild_progress_pct,
            'estimated_time_remaining_hours': (100 - array.rebuild_progress_pct) * 0.1,
        }
    
    def complete_rebuild(self, array_id: str = 'primary') -> bool:
        """Complete a rebuild operation."""
        array = self._arrays.get(array_id)
        if not array:
            return False
        
        if array.status != ArrayStatus.REBUILDING:
            return False
        
        array.status = ArrayStatus.OPTIMAL
        array.rebuild_progress_pct = None
        
        logger.info(f"Rebuild completed for array {array_id}")
        return True
    
    def run_scrub(self, array_id: str = 'primary') -> Dict:
        """Run data scrubbing/verification."""
        array = self._arrays.get(array_id)
        if not array:
            return {'error': 'Array not found'}
        
        # Simulate scrub results
        return {
            'array_id': array_id,
            'started': datetime.now().isoformat(),
            'status': 'completed',
            'errors_found': 0,
            'errors_corrected': 0,
            'blocks_scanned': 1000000000,
            'duration_hours': 4.5,
        }

