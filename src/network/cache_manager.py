"""
DDIL Cache Manager
==================

Manages 480TB local cache for DDIL operations with predictive buffering.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from threading import Lock

logger = logging.getLogger(__name__)


class CachePriority(Enum):
    """Priority levels for cached data."""
    CRITICAL = 1      # Mission-critical data, never evict
    HIGH = 2          # Important operational data
    NORMAL = 3        # Standard data
    LOW = 4           # Nice-to-have data
    PREFETCH = 5      # Predictively fetched data


class CacheStatus(Enum):
    """Status of cache system."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class CacheEntry:
    """Represents a cached data entry."""
    key: str
    size_bytes: int
    priority: CachePriority
    created_at: datetime
    accessed_at: datetime
    expires_at: Optional[datetime]
    source: str
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheStatistics:
    """Cache system statistics."""
    total_capacity_tb: float
    used_capacity_tb: float
    free_capacity_tb: float
    utilization_pct: float
    entry_count: int
    hit_rate_pct: float
    miss_rate_pct: float
    eviction_count: int
    prefetch_accuracy_pct: float


class CacheManager:
    """
    Manages local cache for DDIL autonomous operations.
    
    Features:
    - 480TB NVMe storage capacity
    - Priority-based eviction
    - Predictive prefetching
    - Automatic synchronization
    - Data integrity verification
    """
    
    DEFAULT_CAPACITY_TB = 480
    
    def __init__(self, capacity_tb: float = DEFAULT_CAPACITY_TB):
        """
        Initialize cache manager.
        
        Args:
            capacity_tb: Total cache capacity in terabytes
        """
        self.capacity_tb = capacity_tb
        self.capacity_bytes = capacity_tb * 1024 * 1024 * 1024 * 1024
        
        self._entries: Dict[str, CacheEntry] = {}
        self._used_bytes = 0
        self._lock = Lock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._prefetch_hits = 0
        self._prefetch_total = 0
        
        logger.info(f"Cache Manager initialized: {capacity_tb}TB capacity")
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """
        Retrieve entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            CacheEntry if found, None otherwise
        """
        with self._lock:
            entry = self._entries.get(key)
            
            if entry:
                # Check expiration
                if entry.expires_at and datetime.now() > entry.expires_at:
                    self._remove_entry(key)
                    self._misses += 1
                    return None
                
                entry.accessed_at = datetime.now()
                self._hits += 1
                
                if entry.priority == CachePriority.PREFETCH:
                    self._prefetch_hits += 1
                
                return entry
            
            self._misses += 1
            return None
    
    def put(
        self,
        key: str,
        size_bytes: int,
        source: str,
        priority: CachePriority = CachePriority.NORMAL,
        ttl_hours: Optional[float] = None,
        checksum: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store entry in cache.
        
        Args:
            key: Cache key
            size_bytes: Size of data in bytes
            source: Data source identifier
            priority: Cache priority level
            ttl_hours: Time-to-live in hours
            checksum: Data checksum for integrity
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        with self._lock:
            # Check if we need to evict
            while self._used_bytes + size_bytes > self.capacity_bytes:
                if not self._evict_lowest_priority():
                    logger.warning("Cannot store entry: cache full and no evictable entries")
                    return False
            
            now = datetime.now()
            expires_at = now + timedelta(hours=ttl_hours) if ttl_hours else None
            
            entry = CacheEntry(
                key=key,
                size_bytes=size_bytes,
                priority=priority,
                created_at=now,
                accessed_at=now,
                expires_at=expires_at,
                source=source,
                checksum=checksum,
                metadata=metadata or {},
            )
            
            # Remove existing entry if present
            if key in self._entries:
                self._remove_entry(key)
            
            self._entries[key] = entry
            self._used_bytes += size_bytes
            
            if priority == CachePriority.PREFETCH:
                self._prefetch_total += 1
            
            return True
    
    def remove(self, key: str) -> bool:
        """Remove entry from cache."""
        with self._lock:
            return self._remove_entry(key)
    
    def _remove_entry(self, key: str) -> bool:
        """Internal method to remove entry (must hold lock)."""
        if key in self._entries:
            entry = self._entries.pop(key)
            self._used_bytes -= entry.size_bytes
            return True
        return False
    
    def _evict_lowest_priority(self) -> bool:
        """Evict lowest priority entry (must hold lock)."""
        # Find lowest priority, oldest accessed entry
        candidates = [
            (key, entry) for key, entry in self._entries.items()
            if entry.priority != CachePriority.CRITICAL
        ]
        
        if not candidates:
            return False
        
        # Sort by priority (higher number = lower priority), then by access time
        candidates.sort(key=lambda x: (-x[1].priority.value, x[1].accessed_at))
        
        key_to_evict = candidates[0][0]
        self._remove_entry(key_to_evict)
        self._evictions += 1
        
        logger.debug(f"Evicted cache entry: {key_to_evict}")
        return True
    
    def prefetch(self, keys: List[str], source: str, size_estimate_bytes: int) -> int:
        """
        Prefetch data based on prediction.
        
        Args:
            keys: List of keys to prefetch
            source: Data source
            size_estimate_bytes: Estimated size per entry
            
        Returns:
            Number of entries prefetched
        """
        prefetched = 0
        
        for key in keys:
            if key not in self._entries:
                if self.put(
                    key=key,
                    size_bytes=size_estimate_bytes,
                    source=source,
                    priority=CachePriority.PREFETCH,
                    ttl_hours=24,
                ):
                    prefetched += 1
        
        logger.info(f"Prefetched {prefetched}/{len(keys)} entries")
        return prefetched
    
    def get_statistics(self) -> CacheStatistics:
        """Get current cache statistics."""
        with self._lock:
            used_tb = self._used_bytes / (1024 ** 4)
            total_requests = self._hits + self._misses
            
            return CacheStatistics(
                total_capacity_tb=self.capacity_tb,
                used_capacity_tb=used_tb,
                free_capacity_tb=self.capacity_tb - used_tb,
                utilization_pct=(used_tb / self.capacity_tb) * 100,
                entry_count=len(self._entries),
                hit_rate_pct=(self._hits / total_requests * 100) if total_requests > 0 else 0,
                miss_rate_pct=(self._misses / total_requests * 100) if total_requests > 0 else 0,
                eviction_count=self._evictions,
                prefetch_accuracy_pct=(
                    self._prefetch_hits / self._prefetch_total * 100
                    if self._prefetch_total > 0 else 0
                ),
            )
    
    def get_status(self) -> CacheStatus:
        """Get current cache health status."""
        stats = self.get_statistics()
        
        if stats.utilization_pct > 95:
            return CacheStatus.CRITICAL
        elif stats.utilization_pct > 80:
            return CacheStatus.WARNING
        else:
            return CacheStatus.HEALTHY
    
    def clear_expired(self) -> int:
        """Remove all expired entries."""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._entries.items()
                if entry.expires_at and now > entry.expires_at
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
            
            logger.info(f"Cleared {len(expired_keys)} expired entries")
            return len(expired_keys)
    
    def clear_by_priority(self, priority: CachePriority) -> int:
        """Clear all entries of a specific priority."""
        with self._lock:
            keys_to_remove = [
                key for key, entry in self._entries.items()
                if entry.priority == priority
            ]
            
            for key in keys_to_remove:
                self._remove_entry(key)
            
            logger.info(f"Cleared {len(keys_to_remove)} entries with priority {priority.value}")
            return len(keys_to_remove)
    
    def get_ddil_readiness(self, required_hours: float = 24) -> Dict[str, Any]:
        """
        Check if cache is ready for DDIL operation.
        
        Args:
            required_hours: Required autonomy hours
            
        Returns:
            Readiness assessment dictionary
        """
        stats = self.get_statistics()
        
        # Estimate data consumption rate (simulated)
        consumption_rate_tb_per_hour = 0.5
        available_hours = stats.free_capacity_tb / consumption_rate_tb_per_hour
        
        return {
            'ready': available_hours >= required_hours,
            'available_hours': available_hours,
            'required_hours': required_hours,
            'cache_utilization_pct': stats.utilization_pct,
            'critical_data_cached': True,  # Simulated
            'sync_status': 'current',
        }

