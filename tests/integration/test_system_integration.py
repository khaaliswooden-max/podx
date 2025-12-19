"""
Integration tests for PodX system components.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.orchestrator import SystemOrchestrator, SystemState
from core.config_manager import ConfigManager
from monitoring.system_monitor import SystemMonitor, HealthStatus
from benchmark.xdop_engine import XdoPBenchmarkEngine


class TestSystemIntegration:
    """Integration tests for system components."""
    
    def test_orchestrator_with_monitor(self):
        """Test orchestrator with system monitor."""
        orchestrator = SystemOrchestrator()
        monitor = SystemMonitor()
        
        orchestrator.register_subsystem('monitor', monitor)
        
        status = orchestrator.get_status()
        assert 'monitor' in status['subsystems']
    
    def test_config_manager_integration(self):
        """Test configuration manager with system."""
        config = ConfigManager()
        
        assert config.config.xdop_compliance_level == 'strict'
        assert config.config.simulation_mode is True
        
        validation = config.validate()
        assert validation['valid'] is True
    
    def test_benchmark_with_config(self):
        """Test benchmark engine respects configuration."""
        config = ConfigManager()
        engine = XdoPBenchmarkEngine(config={'simulation': True})
        
        result = engine.run_full_benchmark(simulation_mode=True)
        assert result.wcbi_score >= 85
    
    def test_monitor_health_tracking(self):
        """Test system monitor health tracking."""
        monitor = SystemMonitor()
        
        # Manually collect metrics
        monitor._collect_metrics()
        monitor._evaluate_health()
        
        health = monitor.get_system_health()
        assert health.overall_status in [HealthStatus.HEALTHY, HealthStatus.WARNING]
    
    def test_full_system_startup(self):
        """Test full system startup sequence."""
        orchestrator = SystemOrchestrator()
        monitor = SystemMonitor()
        
        orchestrator.register_subsystem('monitor', monitor)
        
        # Start system
        success = orchestrator.start()
        assert success is True
        assert orchestrator.state == SystemState.OPERATIONAL
        
        # Stop system
        orchestrator.stop()
        assert orchestrator.state == SystemState.SHUTDOWN


class TestXdoPCompliance:
    """Integration tests for XdoP compliance."""
    
    def test_level_3_requirements(self):
        """Test all Level 3 requirements are met."""
        engine = XdoPBenchmarkEngine()
        result = engine.run_full_benchmark(simulation_mode=True)
        
        # Check overall WCBI
        assert result.wcbi_score >= 85, f"WCBI {result.wcbi_score} < 85"
        
        # Check all domains meet minimum
        for domain_result in result.domain_results:
            assert domain_result.raw_score >= 80, \
                f"{domain_result.domain_name} score {domain_result.raw_score} < 80"
    
    def test_ddil_autonomy(self):
        """Test DDIL autonomy meets requirements."""
        from network.ddil_controller import DDILController
        
        controller = DDILController(autonomy_hours=24)
        status = controller.get_status()
        
        assert status.ddil_autonomy_remaining_hours >= 12
    
    def test_certification_readiness(self):
        """Test certification readiness."""
        from benchmark.certification import CertificationManager
        
        cert_manager = CertificationManager()
        record = cert_manager.initialize_certification("TEST-001")
        
        # Update requirements with passing values
        cert_manager.update_requirement('L3-001', 100)  # WCBI
        cert_manager.update_requirement('L3-002', 100)  # Min domain
        cert_manager.update_requirement('L3-003', 24)   # DDIL hours
        cert_manager.update_requirement('L3-004', True)  # MIL-STD
        cert_manager.update_requirement('L3-005', True)  # Audit
        cert_manager.update_requirement('L3-006', 99.99) # Availability
        cert_manager.update_requirement('L3-007', 10)    # Frameworks
        cert_manager.update_requirement('L3-008', 100)   # Renewable
        
        readiness = cert_manager.evaluate_certification_readiness()
        assert readiness['ready'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

