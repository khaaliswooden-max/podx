"""
PodX XdoP Benchmark Engine
==========================

This module implements the XdoP (eXtreme Distributed Operations Protocol) benchmark
framework for validating PodX system compliance across all seven domains.

Domains:
    1. Mobility & Network (20% weight)
    2. Energy & Power (18% weight)
    3. Reliability & Availability (17% weight)
    4. Compute Performance (15% weight)
    5. Security & Compliance (12% weight)
    6. Ruggedization (10% weight)
    7. Sustainability & TCO (8% weight)
"""

from .xdop_engine import XdoPBenchmarkEngine
from .domain_benchmarks import (
    MobilityNetworkBenchmark,
    EnergyPowerBenchmark,
    ReliabilityBenchmark,
    ComputePerformanceBenchmark,
    SecurityComplianceBenchmark,
    RuggedizationBenchmark,
    SustainabilityBenchmark,
)
from .wcbi_calculator import WCBICalculator
from .certification import CertificationManager

__all__ = [
    'XdoPBenchmarkEngine',
    'MobilityNetworkBenchmark',
    'EnergyPowerBenchmark',
    'ReliabilityBenchmark',
    'ComputePerformanceBenchmark',
    'SecurityComplianceBenchmark',
    'RuggedizationBenchmark',
    'SustainabilityBenchmark',
    'WCBICalculator',
    'CertificationManager',
]

__version__ = '1.0.0'


