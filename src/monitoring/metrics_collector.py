"""
Metrics Collector
=================

Collects and stores system metrics for analysis and reporting.
"""

import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


class MetricsCollector:
    """
    Collects and stores time-series metrics.
    
    Features:
    - Configurable retention period
    - Aggregation functions
    - Export capabilities
    """
    
    DEFAULT_RETENTION_HOURS = 24
    DEFAULT_MAX_POINTS = 86400  # 1 point per second for 24 hours
    
    def __init__(
        self,
        retention_hours: float = DEFAULT_RETENTION_HOURS,
        max_points: int = DEFAULT_MAX_POINTS
    ):
        """
        Initialize metrics collector.
        
        Args:
            retention_hours: Hours to retain metrics
            max_points: Maximum points per metric
        """
        self.retention_hours = retention_hours
        self.max_points = max_points
        
        self._metrics: Dict[str, deque] = {}
        self._lock = Lock()
        
        logger.info(f"Metrics Collector initialized: {retention_hours}h retention")
    
    def record(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for the metric
        """
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {},
        )
        
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = deque(maxlen=self.max_points)
            
            self._metrics[metric_name].append(point)
    
    def get_latest(self, metric_name: str) -> Optional[MetricPoint]:
        """Get the latest value for a metric."""
        with self._lock:
            if metric_name in self._metrics and self._metrics[metric_name]:
                return self._metrics[metric_name][-1]
        return None
    
    def get_series(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MetricPoint]:
        """
        Get time series data for a metric.
        
        Args:
            metric_name: Name of the metric
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of MetricPoint objects
        """
        with self._lock:
            if metric_name not in self._metrics:
                return []
            
            points = list(self._metrics[metric_name])
        
        if start_time:
            points = [p for p in points if p.timestamp >= start_time]
        if end_time:
            points = [p for p in points if p.timestamp <= end_time]
        
        return points
    
    def get_average(
        self,
        metric_name: str,
        window_minutes: float = 5
    ) -> Optional[float]:
        """
        Get average value over a time window.
        
        Args:
            metric_name: Name of the metric
            window_minutes: Time window in minutes
            
        Returns:
            Average value or None if no data
        """
        start_time = datetime.now() - timedelta(minutes=window_minutes)
        points = self.get_series(metric_name, start_time=start_time)
        
        if not points:
            return None
        
        return sum(p.value for p in points) / len(points)
    
    def get_min_max(
        self,
        metric_name: str,
        window_minutes: float = 60
    ) -> Optional[Dict[str, float]]:
        """
        Get min/max values over a time window.
        
        Args:
            metric_name: Name of the metric
            window_minutes: Time window in minutes
            
        Returns:
            Dict with 'min' and 'max' keys or None
        """
        start_time = datetime.now() - timedelta(minutes=window_minutes)
        points = self.get_series(metric_name, start_time=start_time)
        
        if not points:
            return None
        
        values = [p.value for p in points]
        return {
            'min': min(values),
            'max': max(values),
            'count': len(values),
        }
    
    def get_percentile(
        self,
        metric_name: str,
        percentile: float,
        window_minutes: float = 60
    ) -> Optional[float]:
        """
        Get percentile value over a time window.
        
        Args:
            metric_name: Name of the metric
            percentile: Percentile (0-100)
            window_minutes: Time window in minutes
            
        Returns:
            Percentile value or None
        """
        start_time = datetime.now() - timedelta(minutes=window_minutes)
        points = self.get_series(metric_name, start_time=start_time)
        
        if not points:
            return None
        
        values = sorted(p.value for p in points)
        index = int(len(values) * percentile / 100)
        return values[min(index, len(values) - 1)]
    
    def list_metrics(self) -> List[str]:
        """List all metric names."""
        with self._lock:
            return list(self._metrics.keys())
    
    def get_statistics(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Dictionary of statistics or None
        """
        with self._lock:
            if metric_name not in self._metrics:
                return None
            
            points = list(self._metrics[metric_name])
        
        if not points:
            return None
        
        values = [p.value for p in points]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'average': sum(values) / len(values),
            'latest': values[-1],
            'first_timestamp': points[0].timestamp.isoformat(),
            'last_timestamp': points[-1].timestamp.isoformat(),
        }
    
    def cleanup_old_data(self) -> int:
        """
        Remove data older than retention period.
        
        Returns:
            Number of points removed
        """
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        removed = 0
        
        with self._lock:
            for metric_name in self._metrics:
                original_len = len(self._metrics[metric_name])
                self._metrics[metric_name] = deque(
                    (p for p in self._metrics[metric_name] if p.timestamp >= cutoff),
                    maxlen=self.max_points
                )
                removed += original_len - len(self._metrics[metric_name])
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} old metric points")
        
        return removed
    
    def export_json(self, metric_name: str) -> List[Dict[str, Any]]:
        """Export metric data as JSON-serializable list."""
        points = self.get_series(metric_name)
        return [
            {
                'timestamp': p.timestamp.isoformat(),
                'value': p.value,
                'tags': p.tags,
            }
            for p in points
        ]


