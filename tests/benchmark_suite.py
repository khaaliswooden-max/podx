#!/usr/bin/env python3
"""
XdoP Benchmark Suite
====================

Command-line tool for running XdoP compliance benchmarks.
"""

import argparse
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from benchmark.xdop_engine import XdoPBenchmarkEngine, ComplianceLevel
from benchmark.wcbi_calculator import WCBICalculator


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def run_full_benchmark(args):
    """Run complete XdoP benchmark."""
    print("\n" + "="*70)
    print("PODX XDOP BENCHMARK SUITE")
    print("="*70 + "\n")
    
    engine = XdoPBenchmarkEngine()
    
    print("Running full benchmark across all 7 domains...\n")
    
    result = engine.run_full_benchmark(simulation_mode=not args.real)
    
    # Generate report
    report = engine.generate_report(result)
    print(report)
    
    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report)
        print(f"\nReport saved to: {args.output}")
    
    # Export JSON if requested
    if args.json:
        engine.export_results_json(result, args.json)
        print(f"JSON results saved to: {args.json}")
    
    # Generate certification report if requested
    if args.report:
        generate_certification_report(result, args.report)
    
    # Return exit code based on compliance
    if result.compliance_level == ComplianceLevel.LEVEL_3_MISSION_CRITICAL:
        print("\n✅ LEVEL 3 MISSION CRITICAL COMPLIANCE ACHIEVED")
        return 0
    else:
        print(f"\n⚠️ Compliance Level: {result.compliance_level.value}")
        return 1


def run_domain_benchmark(args):
    """Run benchmark for a specific domain."""
    print(f"\nRunning benchmark for domain: {args.domain}\n")
    
    engine = XdoPBenchmarkEngine()
    
    try:
        result = engine.run_domain_benchmark(args.domain, simulation_mode=not args.real)
        
        print(f"Domain: {result.domain_name}")
        print(f"Weight: {result.weight * 100:.0f}%")
        print(f"Score: {result.raw_score:.1f}/100")
        print(f"Weighted: {result.weighted_score:.2f}")
        print(f"Status: {'PASS ✓' if result.passed else 'FAIL ✗'}")
        
        if result.metrics:
            print("\nMetrics:")
            for key, value in result.metrics.items():
                print(f"  {key}: {value}")
        
        return 0 if result.passed else 1
        
    except ValueError as e:
        print(f"Error: {e}")
        return 1


def generate_certification_report(result, output_path: str):
    """Generate detailed certification report."""
    report_lines = [
        "PODX XDOP LEVEL 3 CERTIFICATION REPORT",
        "="*50,
        f"Generated: {datetime.now().isoformat()}",
        "",
        "EXECUTIVE SUMMARY",
        "-"*50,
        f"WCBI Score: {result.wcbi_score:.1f}/100",
        f"Compliance Level: {result.compliance_level.value}",
        f"Certification Ready: {'Yes' if result.certification_ready else 'No'}",
        "",
        "DOMAIN BREAKDOWN",
        "-"*50,
    ]
    
    for dr in result.domain_results:
        status = "✓" if dr.passed else "✗"
        report_lines.append(f"{dr.domain_name}: {dr.raw_score:.1f}/100 [{status}]")
    
    report_lines.extend([
        "",
        "LEVEL 3 REQUIREMENTS",
        "-"*50,
        f"Overall WCBI ≥85: {'✓' if result.wcbi_score >= 85 else '✗'} ({result.wcbi_score:.1f})",
        f"All Domains ≥80: {'✓' if result.overall_passed else '✗'}",
        "",
        "RECOMMENDATION",
        "-"*50,
    ])
    
    if result.certification_ready:
        report_lines.append("System is READY for XdoP Level 3 certification audit.")
    else:
        report_lines.append("System requires improvements before certification.")
        failed = [dr for dr in result.domain_results if not dr.passed]
        if failed:
            report_lines.append("Domains requiring attention:")
            for dr in failed:
                report_lines.append(f"  - {dr.domain_name}: {dr.raw_score:.1f}/100")
    
    report_content = "\n".join(report_lines)
    
    Path(output_path).write_text(report_content)
    print(f"\nCertification report saved to: {output_path}")


def list_domains():
    """List available benchmark domains."""
    print("\nAvailable XdoP Benchmark Domains:")
    print("-"*40)
    
    engine = XdoPBenchmarkEngine()
    for domain, weight in engine.DOMAIN_WEIGHTS.items():
        print(f"  {domain}: {weight*100:.0f}% weight")


def main():
    parser = argparse.ArgumentParser(
        description='PodX XdoP Benchmark Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark_suite.py --full
  python benchmark_suite.py --domain mobility_network
  python benchmark_suite.py --full --report certification.txt
  python benchmark_suite.py --full --json results.json
        """
    )
    
    parser.add_argument('--full', action='store_true',
                        help='Run full benchmark across all domains')
    parser.add_argument('--domain', type=str,
                        help='Run benchmark for specific domain')
    parser.add_argument('--list', action='store_true',
                        help='List available domains')
    parser.add_argument('--output', '-o', type=str,
                        help='Output file for report')
    parser.add_argument('--json', type=str,
                        help='Export results as JSON')
    parser.add_argument('--report', type=str,
                        help='Generate certification report')
    parser.add_argument('--real', action='store_true',
                        help='Use real hardware (default: simulation)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if args.list:
        list_domains()
        return 0
    elif args.domain:
        return run_domain_benchmark(args)
    elif args.full:
        return run_full_benchmark(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())


