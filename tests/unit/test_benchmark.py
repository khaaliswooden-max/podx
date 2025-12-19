"""
Unit tests for XdoP Benchmark Engine.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from benchmark.xdop_engine import XdoPBenchmarkEngine, ComplianceLevel
from benchmark.wcbi_calculator import WCBICalculator
from benchmark.domain_benchmarks import (
    MobilityNetworkBenchmark,
    EnergyPowerBenchmark,
    ReliabilityBenchmark,
)


class TestXdoPBenchmarkEngine:
    """Tests for XdoPBenchmarkEngine."""
    
    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        engine = XdoPBenchmarkEngine()
        assert engine is not None
        assert len(engine.DOMAIN_WEIGHTS) == 7
        
    def test_domain_weights_sum_to_one(self):
        """Test that domain weights sum to 1.0."""
        engine = XdoPBenchmarkEngine()
        total = sum(engine.DOMAIN_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001
    
    def test_run_full_benchmark(self):
        """Test running full benchmark in simulation mode."""
        engine = XdoPBenchmarkEngine()
        result = engine.run_full_benchmark(simulation_mode=True)
        
        assert result is not None
        assert result.wcbi_score >= 0
        assert result.wcbi_score <= 100
        assert len(result.domain_results) == 7
    
    def test_benchmark_achieves_level_3(self):
        """Test that simulation achieves Level 3 compliance."""
        engine = XdoPBenchmarkEngine()
        result = engine.run_full_benchmark(simulation_mode=True)
        
        assert result.wcbi_score >= 85
        assert result.compliance_level == ComplianceLevel.LEVEL_3_MISSION_CRITICAL
    
    def test_run_single_domain(self):
        """Test running a single domain benchmark."""
        engine = XdoPBenchmarkEngine()
        result = engine.run_domain_benchmark('mobility_network', simulation_mode=True)
        
        assert result is not None
        assert result.domain_name == 'mobility_network'
        assert result.raw_score >= 0
        assert result.raw_score <= 100
    
    def test_invalid_domain_raises_error(self):
        """Test that invalid domain name raises ValueError."""
        engine = XdoPBenchmarkEngine()
        
        with pytest.raises(ValueError):
            engine.run_domain_benchmark('invalid_domain')
    
    def test_generate_report(self):
        """Test report generation."""
        engine = XdoPBenchmarkEngine()
        result = engine.run_full_benchmark(simulation_mode=True)
        report = engine.generate_report(result)
        
        assert "XDOP BENCHMARK REPORT" in report
        assert "WCBI Score" in report


class TestWCBICalculator:
    """Tests for WCBICalculator."""
    
    def test_calculator_initialization(self):
        """Test calculator initializes correctly."""
        calc = WCBICalculator()
        assert calc is not None
        assert len(calc.weights) == 7
    
    def test_perfect_scores(self):
        """Test WCBI calculation with perfect scores."""
        calc = WCBICalculator()
        
        perfect_scores = {
            'mobility_network': 100,
            'energy_power': 100,
            'reliability': 100,
            'compute_performance': 100,
            'security_compliance': 100,
            'ruggedization': 100,
            'sustainability_tco': 100,
        }
        
        result = calc.calculate(perfect_scores)
        
        assert result.total_score == 100
        assert result.level_3_compliant is True
    
    def test_level_3_threshold(self):
        """Test Level 3 threshold detection."""
        calc = WCBICalculator()
        
        # Just below threshold
        below_threshold = {domain: 84 for domain in calc.weights}
        result = calc.calculate(below_threshold)
        assert result.level_3_compliant is False
        
        # At threshold
        at_threshold = {domain: 85 for domain in calc.weights}
        result = calc.calculate(at_threshold)
        assert result.level_3_compliant is True
    
    def test_scorecard_generation(self):
        """Test scorecard string generation."""
        calc = WCBICalculator()
        scores = {domain: 100 for domain in calc.weights}
        result = calc.calculate(scores)
        scorecard = calc.generate_scorecard(result)
        
        assert "WCBI SCORECARD" in scorecard
        assert "100.0/100" in scorecard


class TestDomainBenchmarks:
    """Tests for individual domain benchmarks."""
    
    def test_mobility_network_benchmark(self):
        """Test mobility & network benchmark."""
        benchmark = MobilityNetworkBenchmark()
        score, metrics = benchmark.run(simulation_mode=True)
        
        assert score >= 0
        assert score <= 100
        assert 'redeployment_time_min' in metrics
        assert 'handover_latency_ms' in metrics
        assert 'ddil_autonomy_hours' in metrics
    
    def test_energy_power_benchmark(self):
        """Test energy & power benchmark."""
        benchmark = EnergyPowerBenchmark()
        score, metrics = benchmark.run(simulation_mode=True)
        
        assert score >= 0
        assert score <= 100
        assert 'solar_efficiency_pct' in metrics
        assert 'battery_backup_hours' in metrics
    
    def test_reliability_benchmark(self):
        """Test reliability benchmark."""
        benchmark = ReliabilityBenchmark()
        score, metrics = benchmark.run(simulation_mode=True)
        
        assert score >= 0
        assert score <= 100
        assert 'availability_pct' in metrics
        assert 'mtbf_hours' in metrics


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

