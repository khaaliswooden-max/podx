"""
Unit tests for Network module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from network.ddil_controller import DDILController, NetworkMode, ConnectionState
from network.handover_manager import HandoverManager, HandoverStrategy
from network.cache_manager import CacheManager, CachePriority


class TestDDILController:
    """Tests for DDIL Controller."""
    
    def test_controller_initialization(self):
        """Test controller initializes correctly."""
        controller = DDILController()
        assert controller is not None
        assert controller.autonomy_hours == 24
        assert controller.cache_size_tb == 480
    
    def test_paths_initialized(self):
        """Test network paths are initialized."""
        controller = DDILController()
        assert len(controller.paths) > 0
        assert NetworkMode.SATELLITE in controller.paths
        assert NetworkMode.CELLULAR_5G in controller.paths
    
    def test_get_status(self):
        """Test getting DDIL status."""
        controller = DDILController()
        status = controller.get_status()
        
        assert status is not None
        assert hasattr(status, 'mode')
        assert hasattr(status, 'ddil_autonomy_remaining_hours')
    
    def test_enable_disable_path(self):
        """Test enabling and disabling paths."""
        controller = DDILController()
        
        controller.disable_path(NetworkMode.SATELLITE)
        assert controller.paths[NetworkMode.SATELLITE].enabled is False
        
        controller.enable_path(NetworkMode.SATELLITE)
        assert controller.paths[NetworkMode.SATELLITE].enabled is True
    
    def test_get_path_metrics(self):
        """Test getting path metrics."""
        controller = DDILController()
        metrics = controller.get_path_metrics(NetworkMode.SATELLITE)
        
        assert metrics is not None
        assert 'mode' in metrics
        assert 'latency_ms' in metrics


class TestHandoverManager:
    """Tests for Handover Manager."""
    
    def test_manager_initialization(self):
        """Test manager initializes correctly."""
        manager = HandoverManager()
        assert manager is not None
        assert manager.strategy == HandoverStrategy.MAKE_BEFORE_BREAK
    
    def test_execute_handover(self):
        """Test executing a handover."""
        manager = HandoverManager()
        metrics = manager.execute_handover("satellite", "cellular_5g")
        
        assert metrics is not None
        assert metrics.success is True
        assert metrics.duration_ms < 200  # Should be under target
    
    def test_handover_statistics(self):
        """Test getting handover statistics."""
        manager = HandoverManager()
        
        # Execute a few handovers
        manager.execute_handover("a", "b")
        manager.execute_handover("b", "c")
        
        stats = manager.get_statistics()
        
        assert stats['total_handovers'] == 2
        assert stats['successful'] == 2
    
    def test_meets_target_latency(self):
        """Test target latency check."""
        manager = HandoverManager()
        manager.execute_handover("a", "b")
        
        assert manager.meets_target_latency() is True


class TestCacheManager:
    """Tests for Cache Manager."""
    
    def test_manager_initialization(self):
        """Test manager initializes correctly."""
        manager = CacheManager(capacity_tb=100)
        assert manager is not None
        assert manager.capacity_tb == 100
    
    def test_put_and_get(self):
        """Test storing and retrieving cache entries."""
        manager = CacheManager(capacity_tb=1)
        
        success = manager.put(
            key="test_key",
            size_bytes=1024,
            source="test",
            priority=CachePriority.NORMAL,
        )
        assert success is True
        
        entry = manager.get("test_key")
        assert entry is not None
        assert entry.key == "test_key"
    
    def test_get_nonexistent(self):
        """Test getting nonexistent entry."""
        manager = CacheManager()
        entry = manager.get("nonexistent")
        assert entry is None
    
    def test_cache_statistics(self):
        """Test getting cache statistics."""
        manager = CacheManager()
        manager.put("key1", 1024, "test")
        manager.get("key1")  # Hit
        manager.get("key2")  # Miss
        
        stats = manager.get_statistics()
        
        assert stats.entry_count == 1
        assert stats.hit_rate_pct > 0
    
    def test_ddil_readiness(self):
        """Test DDIL readiness check."""
        manager = CacheManager()
        readiness = manager.get_ddil_readiness(required_hours=24)
        
        assert 'ready' in readiness
        assert 'available_hours' in readiness


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


