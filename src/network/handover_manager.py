"""
Network Handover Manager
========================

Manages seamless network transitions with <100ms handover latency.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable
from threading import Lock

logger = logging.getLogger(__name__)


class HandoverStrategy(Enum):
    """Network handover strategies."""
    MAKE_BEFORE_BREAK = "make_before_break"  # Establish new before dropping old
    BREAK_BEFORE_MAKE = "break_before_make"  # Drop old before establishing new
    SEAMLESS = "seamless"                     # Parallel operation during transition


@dataclass
class HandoverMetrics:
    """Metrics from a handover operation."""
    source_path: str
    target_path: str
    strategy: HandoverStrategy
    start_time: datetime
    end_time: datetime
    duration_ms: float
    packets_lost: int
    success: bool
    error_message: Optional[str] = None


class HandoverManager:
    """
    Manages network path transitions with minimal disruption.
    
    Implements make-before-break handover to achieve <100ms transitions
    between network paths while maintaining session continuity.
    """
    
    TARGET_HANDOVER_MS = 100  # Target handover time
    MAX_HANDOVER_MS = 200     # Maximum acceptable handover time
    
    def __init__(self, strategy: HandoverStrategy = HandoverStrategy.MAKE_BEFORE_BREAK):
        """
        Initialize handover manager.
        
        Args:
            strategy: Default handover strategy to use
        """
        self.strategy = strategy
        self.handover_history: List[HandoverMetrics] = []
        self._lock = Lock()
        self._callbacks: List[Callable[[HandoverMetrics], None]] = []
        
        logger.info(f"Handover Manager initialized with strategy: {strategy.value}")
    
    def execute_handover(
        self,
        source_path: str,
        target_path: str,
        strategy: Optional[HandoverStrategy] = None
    ) -> HandoverMetrics:
        """
        Execute network handover from source to target path.
        
        Args:
            source_path: Current network path identifier
            target_path: Target network path identifier
            strategy: Optional override strategy
            
        Returns:
            HandoverMetrics with operation details
        """
        use_strategy = strategy or self.strategy
        start_time = datetime.now()
        start_perf = time.perf_counter()
        
        logger.info(f"Starting handover: {source_path} -> {target_path} ({use_strategy.value})")
        
        try:
            if use_strategy == HandoverStrategy.MAKE_BEFORE_BREAK:
                packets_lost = self._make_before_break(source_path, target_path)
            elif use_strategy == HandoverStrategy.BREAK_BEFORE_MAKE:
                packets_lost = self._break_before_make(source_path, target_path)
            else:
                packets_lost = self._seamless_handover(source_path, target_path)
            
            end_perf = time.perf_counter()
            duration_ms = (end_perf - start_perf) * 1000
            
            metrics = HandoverMetrics(
                source_path=source_path,
                target_path=target_path,
                strategy=use_strategy,
                start_time=start_time,
                end_time=datetime.now(),
                duration_ms=duration_ms,
                packets_lost=packets_lost,
                success=True,
            )
            
            logger.info(f"Handover complete: {duration_ms:.1f}ms, {packets_lost} packets lost")
            
        except Exception as e:
            end_perf = time.perf_counter()
            duration_ms = (end_perf - start_perf) * 1000
            
            metrics = HandoverMetrics(
                source_path=source_path,
                target_path=target_path,
                strategy=use_strategy,
                start_time=start_time,
                end_time=datetime.now(),
                duration_ms=duration_ms,
                packets_lost=-1,
                success=False,
                error_message=str(e),
            )
            
            logger.error(f"Handover failed: {e}")
        
        with self._lock:
            self.handover_history.append(metrics)
        
        for callback in self._callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        return metrics
    
    def _make_before_break(self, source: str, target: str) -> int:
        """
        Make-before-break handover implementation.
        
        Establishes new connection before dropping old one.
        """
        # Simulate establishing new connection
        time.sleep(0.05)  # 50ms to establish
        
        # Simulate traffic migration
        time.sleep(0.03)  # 30ms to migrate
        
        # Simulate dropping old connection
        time.sleep(0.01)  # 10ms to cleanup
        
        return 0  # No packets lost with make-before-break
    
    def _break_before_make(self, source: str, target: str) -> int:
        """
        Break-before-make handover implementation.
        
        Drops old connection before establishing new one.
        """
        # Simulate dropping old connection
        time.sleep(0.01)
        
        # Gap period (packets may be lost)
        time.sleep(0.02)
        
        # Simulate establishing new connection
        time.sleep(0.05)
        
        return 2  # Some packets lost during gap
    
    def _seamless_handover(self, source: str, target: str) -> int:
        """
        Seamless handover with parallel operation.
        
        Both paths active during transition.
        """
        # Simulate parallel operation setup
        time.sleep(0.03)
        
        # Simulate gradual traffic shift
        time.sleep(0.04)
        
        # Simulate cleanup
        time.sleep(0.01)
        
        return 0  # No packets lost
    
    def get_average_handover_time(self) -> float:
        """Get average handover time in milliseconds."""
        with self._lock:
            if not self.handover_history:
                return 0.0
            
            successful = [h for h in self.handover_history if h.success]
            if not successful:
                return 0.0
            
            return sum(h.duration_ms for h in successful) / len(successful)
    
    def get_handover_success_rate(self) -> float:
        """Get handover success rate as percentage."""
        with self._lock:
            if not self.handover_history:
                return 100.0
            
            successful = sum(1 for h in self.handover_history if h.success)
            return (successful / len(self.handover_history)) * 100
    
    def meets_target_latency(self) -> bool:
        """Check if average handover meets target latency."""
        return self.get_average_handover_time() <= self.TARGET_HANDOVER_MS
    
    def register_callback(self, callback: Callable[[HandoverMetrics], None]) -> None:
        """Register callback for handover events."""
        self._callbacks.append(callback)
    
    def get_statistics(self) -> Dict:
        """Get comprehensive handover statistics."""
        with self._lock:
            if not self.handover_history:
                return {
                    'total_handovers': 0,
                    'successful': 0,
                    'failed': 0,
                    'average_duration_ms': 0,
                    'min_duration_ms': 0,
                    'max_duration_ms': 0,
                    'total_packets_lost': 0,
                    'meets_target': True,
                }
            
            successful = [h for h in self.handover_history if h.success]
            durations = [h.duration_ms for h in successful]
            
            return {
                'total_handovers': len(self.handover_history),
                'successful': len(successful),
                'failed': len(self.handover_history) - len(successful),
                'average_duration_ms': sum(durations) / len(durations) if durations else 0,
                'min_duration_ms': min(durations) if durations else 0,
                'max_duration_ms': max(durations) if durations else 0,
                'total_packets_lost': sum(h.packets_lost for h in successful),
                'meets_target': self.meets_target_latency(),
            }


