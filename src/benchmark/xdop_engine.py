"""
XdoP Benchmark Engine
=====================

Core engine for running XdoP compliance benchmarks and generating certification reports.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """XdoP Compliance certification levels."""
    LEVEL_1_BASIC = "Level 1 - Basic Edge"
    LEVEL_2_STANDARD = "Level 2 - Standard Mobile"
    LEVEL_3_MISSION_CRITICAL = "Level 3 - Mission Critical"


class BenchmarkStatus(Enum):
    """Status of a benchmark run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DomainResult:
    """Result from a single domain benchmark."""
    domain_name: str
    weight: float
    raw_score: float
    weighted_score: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    passed: bool = True
    notes: List[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Complete benchmark result across all domains."""
    timestamp: datetime
    wcbi_score: float
    compliance_level: ComplianceLevel
    domain_results: List[DomainResult]
    overall_passed: bool
    certification_ready: bool
    report_path: Optional[str] = None


class XdoPBenchmarkEngine:
    """
    Main engine for running XdoP compliance benchmarks.
    
    The XdoP benchmark evaluates mobile distributed data centers across
    seven weighted domains to produce a Weighted Composite Benchmark Index (WCBI).
    
    Attributes:
        config: Engine configuration dictionary
        results: List of historical benchmark results
    """
    
    # Domain weights as per XdoP specification
    DOMAIN_WEIGHTS = {
        'mobility_network': 0.20,
        'energy_power': 0.18,
        'reliability': 0.17,
        'compute_performance': 0.15,
        'security_compliance': 0.12,
        'ruggedization': 0.10,
        'sustainability_tco': 0.08,
    }
    
    # Level 3 Mission Critical thresholds
    LEVEL_3_THRESHOLDS = {
        'min_wcbi': 85,
        'min_domain_score': 80,
        'ddil_autonomy_hours': 12,
        'mil_std_required': True,
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the XdoP Benchmark Engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.results: List[BenchmarkResult] = []
        self._benchmarks = {}
        self._initialize_benchmarks()
        logger.info("XdoP Benchmark Engine initialized")
    
    def _initialize_benchmarks(self) -> None:
        """Initialize domain benchmark instances."""
        from .domain_benchmarks import (
            MobilityNetworkBenchmark,
            EnergyPowerBenchmark,
            ReliabilityBenchmark,
            ComputePerformanceBenchmark,
            SecurityComplianceBenchmark,
            RuggedizationBenchmark,
            SustainabilityBenchmark,
        )
        
        self._benchmarks = {
            'mobility_network': MobilityNetworkBenchmark(),
            'energy_power': EnergyPowerBenchmark(),
            'reliability': ReliabilityBenchmark(),
            'compute_performance': ComputePerformanceBenchmark(),
            'security_compliance': SecurityComplianceBenchmark(),
            'ruggedization': RuggedizationBenchmark(),
            'sustainability_tco': SustainabilityBenchmark(),
        }
    
    def run_full_benchmark(self, simulation_mode: bool = True) -> BenchmarkResult:
        """
        Run complete XdoP benchmark across all domains.
        
        Args:
            simulation_mode: If True, use simulated values for hardware metrics
            
        Returns:
            BenchmarkResult containing all domain scores and WCBI
        """
        logger.info("Starting full XdoP benchmark run")
        domain_results = []
        total_weighted_score = 0.0
        all_passed = True
        
        for domain_name, benchmark in self._benchmarks.items():
            weight = self.DOMAIN_WEIGHTS[domain_name]
            
            logger.info(f"Running {domain_name} benchmark (weight: {weight*100:.0f}%)")
            
            try:
                raw_score, metrics = benchmark.run(simulation_mode=simulation_mode)
                weighted_score = raw_score * weight
                passed = raw_score >= self.LEVEL_3_THRESHOLDS['min_domain_score']
                
                result = DomainResult(
                    domain_name=domain_name,
                    weight=weight,
                    raw_score=raw_score,
                    weighted_score=weighted_score,
                    metrics=metrics,
                    passed=passed,
                )
                
                domain_results.append(result)
                total_weighted_score += weighted_score
                
                if not passed:
                    all_passed = False
                    logger.warning(f"{domain_name} failed: score {raw_score} < {self.LEVEL_3_THRESHOLDS['min_domain_score']}")
                else:
                    logger.info(f"{domain_name} passed: score {raw_score}/100")
                    
            except Exception as e:
                logger.error(f"Error running {domain_name} benchmark: {e}")
                result = DomainResult(
                    domain_name=domain_name,
                    weight=weight,
                    raw_score=0,
                    weighted_score=0,
                    passed=False,
                    notes=[f"Benchmark failed: {str(e)}"]
                )
                domain_results.append(result)
                all_passed = False
        
        # Determine compliance level
        wcbi_score = total_weighted_score
        compliance_level = self._determine_compliance_level(wcbi_score, all_passed)
        certification_ready = (
            compliance_level == ComplianceLevel.LEVEL_3_MISSION_CRITICAL and
            all_passed
        )
        
        benchmark_result = BenchmarkResult(
            timestamp=datetime.now(),
            wcbi_score=wcbi_score,
            compliance_level=compliance_level,
            domain_results=domain_results,
            overall_passed=all_passed,
            certification_ready=certification_ready,
        )
        
        self.results.append(benchmark_result)
        
        logger.info(f"Benchmark complete: WCBI={wcbi_score:.1f}, Level={compliance_level.value}")
        
        return benchmark_result
    
    def run_domain_benchmark(self, domain: str, simulation_mode: bool = True) -> DomainResult:
        """
        Run benchmark for a specific domain only.
        
        Args:
            domain: Name of the domain to benchmark
            simulation_mode: If True, use simulated values
            
        Returns:
            DomainResult for the specified domain
        """
        if domain not in self._benchmarks:
            raise ValueError(f"Unknown domain: {domain}. Valid domains: {list(self._benchmarks.keys())}")
        
        benchmark = self._benchmarks[domain]
        weight = self.DOMAIN_WEIGHTS[domain]
        
        raw_score, metrics = benchmark.run(simulation_mode=simulation_mode)
        weighted_score = raw_score * weight
        passed = raw_score >= self.LEVEL_3_THRESHOLDS['min_domain_score']
        
        return DomainResult(
            domain_name=domain,
            weight=weight,
            raw_score=raw_score,
            weighted_score=weighted_score,
            metrics=metrics,
            passed=passed,
        )
    
    def _determine_compliance_level(self, wcbi_score: float, all_domains_passed: bool) -> ComplianceLevel:
        """Determine the compliance level based on WCBI score."""
        if wcbi_score >= 85 and all_domains_passed:
            return ComplianceLevel.LEVEL_3_MISSION_CRITICAL
        elif wcbi_score >= 70:
            return ComplianceLevel.LEVEL_2_STANDARD
        else:
            return ComplianceLevel.LEVEL_1_BASIC
    
    def generate_report(self, result: BenchmarkResult, output_path: Optional[str] = None) -> str:
        """
        Generate a detailed benchmark report.
        
        Args:
            result: BenchmarkResult to generate report from
            output_path: Optional path to save report
            
        Returns:
            Report content as string
        """
        report_lines = [
            "=" * 80,
            "XDOP BENCHMARK REPORT",
            "PodX Mobile Distributed Data Center",
            "=" * 80,
            "",
            f"Timestamp: {result.timestamp.isoformat()}",
            f"WCBI Score: {result.wcbi_score:.1f}/100",
            f"Compliance Level: {result.compliance_level.value}",
            f"Certification Ready: {'Yes' if result.certification_ready else 'No'}",
            "",
            "-" * 80,
            "DOMAIN RESULTS",
            "-" * 80,
        ]
        
        for domain_result in result.domain_results:
            status = "✓ PASS" if domain_result.passed else "✗ FAIL"
            report_lines.extend([
                "",
                f"{domain_result.domain_name.upper().replace('_', ' ')}",
                f"  Weight: {domain_result.weight*100:.0f}%",
                f"  Raw Score: {domain_result.raw_score:.1f}/100",
                f"  Weighted Score: {domain_result.weighted_score:.2f}",
                f"  Status: {status}",
            ])
            
            if domain_result.metrics:
                report_lines.append("  Key Metrics:")
                for key, value in domain_result.metrics.items():
                    report_lines.append(f"    - {key}: {value}")
        
        report_lines.extend([
            "",
            "-" * 80,
            "SUMMARY",
            "-" * 80,
            f"Total WCBI Score: {result.wcbi_score:.1f}/100",
            f"Level 3 Threshold: {self.LEVEL_3_THRESHOLDS['min_wcbi']}/100",
            f"Overall Status: {'PASSED' if result.overall_passed else 'FAILED'}",
            "=" * 80,
        ])
        
        report_content = "\n".join(report_lines)
        
        if output_path:
            Path(output_path).write_text(report_content)
            result.report_path = output_path
            logger.info(f"Report saved to {output_path}")
        
        return report_content
    
    def export_results_json(self, result: BenchmarkResult, output_path: str) -> None:
        """Export benchmark results to JSON format."""
        data = {
            'timestamp': result.timestamp.isoformat(),
            'wcbi_score': result.wcbi_score,
            'compliance_level': result.compliance_level.value,
            'overall_passed': result.overall_passed,
            'certification_ready': result.certification_ready,
            'domains': [
                {
                    'name': dr.domain_name,
                    'weight': dr.weight,
                    'raw_score': dr.raw_score,
                    'weighted_score': dr.weighted_score,
                    'passed': dr.passed,
                    'metrics': dr.metrics,
                }
                for dr in result.domain_results
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Results exported to {output_path}")


def main():
    """Run benchmark from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run XdoP Benchmark')
    parser.add_argument('--domain', help='Run specific domain only')
    parser.add_argument('--output', help='Output path for report')
    parser.add_argument('--json', help='Export results as JSON')
    parser.add_argument('--simulation', action='store_true', default=True,
                        help='Use simulation mode (default: True)')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    engine = XdoPBenchmarkEngine()
    
    if args.domain:
        result = engine.run_domain_benchmark(args.domain, simulation_mode=args.simulation)
        print(f"\n{result.domain_name}: {result.raw_score}/100 ({'PASS' if result.passed else 'FAIL'})")
    else:
        result = engine.run_full_benchmark(simulation_mode=args.simulation)
        report = engine.generate_report(result, args.output)
        print(report)
        
        if args.json:
            engine.export_results_json(result, args.json)


if __name__ == '__main__':
    main()

