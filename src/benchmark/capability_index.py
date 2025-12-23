"""
PodX Capability Index (PCI) - Honest Self-Assessment Framework
===============================================================

NOT a certification. A structured way to measure and communicate
system capabilities at each development stage.

This module provides:
- CapabilityAssertion: Individual capability claims with evidence tracking
- CapabilityDomain: Groups of related capabilities
- PodXCapabilityIndex: Full system assessment with TRL tracking

Usage:
    from src.benchmark.capability_index import PodXCapabilityIndex
    
    pci = PodXCapabilityIndex()
    pci.load_from_file("capabilities.yaml")
    report = pci.generate_report()
    print(report)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


class MaturityLevel(Enum):
    """
    Technology Readiness Level (TRL) adapted for PodX.
    
    Uses NASA TRL scale with practical descriptions.
    """
    TRL_1_CONCEPT = "TRL 1: Basic principles observed"
    TRL_2_FORMULATED = "TRL 2: Technology concept formulated"
    TRL_3_PROOF = "TRL 3: Proof of concept (simulation)"
    TRL_4_LAB = "TRL 4: Component validated in lab"
    TRL_5_RELEVANT = "TRL 5: Component validated in relevant environment"
    TRL_6_PROTOTYPE = "TRL 6: System prototype demonstrated"
    TRL_7_OPERATIONAL = "TRL 7: Prototype in operational environment"
    TRL_8_QUALIFIED = "TRL 8: System complete and qualified"
    TRL_9_PRODUCTION = "TRL 9: System proven in operations"

    @property
    def level(self) -> int:
        """Extract numeric TRL level."""
        return int(self.value.split(":")[0].replace("TRL ", ""))
    
    @classmethod
    def from_level(cls, level: int) -> "MaturityLevel":
        """Create from numeric level."""
        for m in cls:
            if m.level == level:
                return m
        raise ValueError(f"Invalid TRL level: {level}")


class EvidenceType(Enum):
    """Types of evidence that support capability claims."""
    NONE = "none"                    # No evidence
    PAPER = "paper_analysis"         # Calculations, design docs
    SIMULATION = "simulation"        # Software simulation results
    COMPONENT_TEST = "component"     # Individual component tested
    INTEGRATION_TEST = "integration" # Integrated system tested
    FIELD_TEST = "field"             # Real-world operational test
    CERTIFICATION = "certification"  # Third-party certification
    PRODUCTION = "production"        # Production deployment data


@dataclass
class Evidence:
    """Evidence supporting a capability claim."""
    type: EvidenceType
    description: str
    date: Optional[datetime] = None
    url: Optional[str] = None  # Link to test data, video, report
    verified_by: Optional[str] = None  # Who verified this evidence
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "url": self.url,
            "verified_by": self.verified_by,
        }


@dataclass
class CapabilityAssertion:
    """
    A single capability claim with evidence.
    
    This is the core unit of honest self-assessment. Each capability
    must declare what's claimed, what's measured, and what evidence exists.
    """
    name: str
    description: str
    target_value: float
    unit: str
    maturity: MaturityLevel
    
    # Optional - filled in when testing occurs
    measured_value: Optional[float] = None
    evidence: Optional[Evidence] = None
    test_procedure: Optional[str] = None
    gap_description: Optional[str] = None
    
    @property
    def validated(self) -> bool:
        """Check if capability meets target with evidence."""
        if self.measured_value is None:
            return False
        if self.evidence is None or self.evidence.type == EvidenceType.NONE:
            return False
        return self.measured_value >= self.target_value
    
    @property
    def gap(self) -> Optional[float]:
        """Calculate gap between target and measured value."""
        if self.measured_value is None:
            return None
        return self.target_value - self.measured_value
    
    def to_claim_string(self) -> str:
        """Generate human-readable claim with appropriate caveats."""
        if self.maturity.level <= 2:
            return f"{self.name}: {self.target_value} {self.unit} (design target, unvalidated)"
        elif self.maturity.level <= 4:
            if self.measured_value is not None:
                return f"{self.name}: {self.measured_value} {self.unit} (simulation/lab, target: {self.target_value})"
            return f"{self.name}: {self.target_value} {self.unit} (target, simulation pending)"
        elif self.validated:
            return f"{self.name}: {self.measured_value} {self.unit} (validated, TRL {self.maturity.level})"
        elif self.measured_value is not None:
            gap = self.gap
            return f"{self.name}: {self.measured_value}/{self.target_value} {self.unit} (gap: {gap:.1f})"
        else:
            return f"{self.name}: {self.target_value} {self.unit} (TRL {self.maturity.level}, measurement pending)"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "target_value": self.target_value,
            "measured_value": self.measured_value,
            "unit": self.unit,
            "maturity": self.maturity.value,
            "maturity_level": self.maturity.level,
            "validated": self.validated,
            "gap": self.gap,
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "test_procedure": self.test_procedure,
            "gap_description": self.gap_description,
        }


@dataclass
class CapabilityDomain:
    """A group of related capabilities."""
    name: str
    description: str
    weight: float  # Importance weight 0-1
    capabilities: list[CapabilityAssertion] = field(default_factory=list)
    
    @property
    def average_maturity(self) -> float:
        """Calculate average TRL across capabilities."""
        if not self.capabilities:
            return 0
        return sum(c.maturity.level for c in self.capabilities) / len(self.capabilities)
    
    @property
    def min_maturity(self) -> int:
        """Return lowest TRL in domain (bottleneck)."""
        if not self.capabilities:
            return 0
        return min(c.maturity.level for c in self.capabilities)
    
    @property
    def validated_count(self) -> int:
        """Count validated capabilities."""
        return sum(1 for c in self.capabilities if c.validated)
    
    @property
    def validation_rate(self) -> float:
        """Percentage of capabilities validated."""
        if not self.capabilities:
            return 0
        return self.validated_count / len(self.capabilities)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "average_maturity": round(self.average_maturity, 1),
            "min_maturity": self.min_maturity,
            "validated_count": self.validated_count,
            "total_count": len(self.capabilities),
            "validation_rate": round(self.validation_rate * 100, 1),
            "capabilities": [c.to_dict() for c in self.capabilities],
        }


class PodXCapabilityIndex:
    """
    Complete capability assessment for PodX system.
    
    Provides honest, evidence-based assessment of what the system
    can actually do vs. what it aspires to do.
    """
    
    def __init__(self, system_name: str = "PodX Nano v1"):
        self.system_name = system_name
        self.version = "1.0.0"
        self.domains: list[CapabilityDomain] = []
        self.assessment_date: Optional[datetime] = None
        self._initialize_default_domains()
    
    def _initialize_default_domains(self) -> None:
        """Set up default capability domains matching XdoP structure."""
        
        # Domain 1: Mobility & Network
        mobility = CapabilityDomain(
            name="Mobility & Network",
            description="DDIL autonomy and network resilience",
            weight=0.20,
            capabilities=[
                CapabilityAssertion(
                    name="DDIL Autonomy Duration",
                    description="Time system operates without external network",
                    target_value=4.0,
                    unit="hours",
                    maturity=MaturityLevel.TRL_2_FORMULATED,
                    test_procedure="Disconnect all networks, run workload, measure time to shutdown",
                    gap_description="Need battery system and workload testing",
                ),
                CapabilityAssertion(
                    name="Network Handover Latency",
                    description="Time to switch between network paths",
                    target_value=200,
                    unit="ms",
                    maturity=MaturityLevel.TRL_3_PROOF,
                    measured_value=95,  # Simulation result
                    evidence=Evidence(
                        type=EvidenceType.SIMULATION,
                        description="DDIL controller simulation in ddil_controller.py",
                        date=datetime(2024, 12, 1),
                    ),
                    test_procedure="Establish primary link, kill it, measure failover time",
                ),
                CapabilityAssertion(
                    name="Deployment Time",
                    description="Vehicle arrival to operational",
                    target_value=15,
                    unit="minutes",
                    maturity=MaturityLevel.TRL_1_CONCEPT,
                    gap_description="No physical system to test",
                ),
            ],
        )
        
        # Domain 2: Energy & Power
        energy = CapabilityDomain(
            name="Energy & Power",
            description="Power autonomy and efficiency",
            weight=0.18,
            capabilities=[
                CapabilityAssertion(
                    name="Battery Runtime (Typical Load)",
                    description="Operating time on battery at 300W draw",
                    target_value=5.0,
                    unit="hours",
                    maturity=MaturityLevel.TRL_2_FORMULATED,
                    measured_value=6.8,  # Calculated: 2048Wh / 300W
                    evidence=Evidence(
                        type=EvidenceType.PAPER,
                        description="Calculated from EcoFlow Delta 2 Max specs",
                    ),
                    gap_description="Need actual runtime test with real workload",
                ),
                CapabilityAssertion(
                    name="Solar Supplement",
                    description="Power contribution from 200W panel",
                    target_value=150,
                    unit="W average",
                    maturity=MaturityLevel.TRL_1_CONCEPT,
                    gap_description="No solar panel acquired/tested",
                ),
            ],
        )
        
        # Domain 3: Compute Performance
        compute = CapabilityDomain(
            name="Compute Performance",
            description="AI inference and processing capability",
            weight=0.15,
            capabilities=[
                CapabilityAssertion(
                    name="LLM Inference Speed (7B model)",
                    description="Tokens per second on quantized 7B model",
                    target_value=50,
                    unit="tok/s",
                    maturity=MaturityLevel.TRL_2_FORMULATED,
                    gap_description="Need GPU and benchmark testing",
                ),
                CapabilityAssertion(
                    name="INT8 TOPS",
                    description="AI inference compute capacity",
                    target_value=330,
                    unit="TOPS",
                    maturity=MaturityLevel.TRL_2_FORMULATED,
                    measured_value=330,  # RTX 4090 spec
                    evidence=Evidence(
                        type=EvidenceType.PAPER,
                        description="NVIDIA RTX 4090 specifications",
                    ),
                ),
            ],
        )
        
        # Domain 4: Reliability
        reliability = CapabilityDomain(
            name="Reliability",
            description="System availability and fault tolerance",
            weight=0.17,
            capabilities=[
                CapabilityAssertion(
                    name="Graceful Degradation",
                    description="System continues operating when components fail",
                    target_value=1,  # Boolean as 0/1
                    unit="bool",
                    maturity=MaturityLevel.TRL_3_PROOF,
                    evidence=Evidence(
                        type=EvidenceType.SIMULATION,
                        description="Software handles network/power loss gracefully",
                    ),
                ),
            ],
        )
        
        # Domain 5: Environmental
        environmental = CapabilityDomain(
            name="Environmental",
            description="Operating conditions and ruggedization",
            weight=0.10,
            capabilities=[
                CapabilityAssertion(
                    name="Operating Temperature Range",
                    description="Ambient temperature for full operation",
                    target_value=45,
                    unit="C max",
                    maturity=MaturityLevel.TRL_1_CONCEPT,
                    gap_description="No thermal testing performed",
                ),
                CapabilityAssertion(
                    name="Ingress Protection",
                    description="Dust and water resistance",
                    target_value=67,  # IP67
                    unit="IP rating",
                    maturity=MaturityLevel.TRL_2_FORMULATED,
                    measured_value=67,
                    evidence=Evidence(
                        type=EvidenceType.PAPER,
                        description="Pelican 1650 case is rated IP67",
                    ),
                ),
            ],
        )
        
        # Domain 6: Security
        security = CapabilityDomain(
            name="Security",
            description="Data protection and access control",
            weight=0.12,
            capabilities=[
                CapabilityAssertion(
                    name="Encryption at Rest",
                    description="Full disk encryption enabled",
                    target_value=1,
                    unit="bool",
                    maturity=MaturityLevel.TRL_3_PROOF,
                    evidence=Evidence(
                        type=EvidenceType.SIMULATION,
                        description="crypto_engine.py implements encryption abstractions",
                    ),
                ),
            ],
        )
        
        # Domain 7: Sustainability
        sustainability = CapabilityDomain(
            name="Sustainability",
            description="Environmental impact and efficiency",
            weight=0.08,
            capabilities=[
                CapabilityAssertion(
                    name="Renewable Operation Capability",
                    description="Can operate fully on solar power",
                    target_value=1,
                    unit="bool",
                    maturity=MaturityLevel.TRL_2_FORMULATED,
                    gap_description="Need Jetson option for sustainable solar-only operation",
                ),
            ],
        )
        
        self.domains = [mobility, energy, compute, reliability, environmental, security, sustainability]
    
    @property
    def overall_maturity(self) -> float:
        """Calculate weighted average maturity across all domains."""
        if not self.domains:
            return 0
        
        weighted_sum = sum(d.min_maturity * d.weight for d in self.domains)
        total_weight = sum(d.weight for d in self.domains)
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    @property
    def bottleneck_maturity(self) -> int:
        """Return the lowest TRL across the system (true readiness level)."""
        if not self.domains:
            return 0
        all_trls = [c.maturity.level for d in self.domains for c in d.capabilities]
        return min(all_trls) if all_trls else 0
    
    @property
    def total_capabilities(self) -> int:
        return sum(len(d.capabilities) for d in self.domains)
    
    @property
    def validated_capabilities(self) -> int:
        return sum(d.validated_count for d in self.domains)
    
    def generate_report(self) -> str:
        """Generate human-readable capability report."""
        lines = [
            "=" * 70,
            f"PODX CAPABILITY INDEX REPORT",
            f"System: {self.system_name}",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 70,
            "",
            "EXECUTIVE SUMMARY",
            "-" * 70,
            f"Overall System Maturity: TRL {self.bottleneck_maturity} (bottleneck)",
            f"Weighted Average Maturity: TRL {self.overall_maturity:.1f}",
            f"Capabilities Validated: {self.validated_capabilities}/{self.total_capabilities}",
            "",
            "!! DISCLAIMER: This is a self-assessment, not a certification.",
            "   Claims should be verified by third parties before use in proposals.",
            "",
        ]
        
        for domain in self.domains:
            lines.extend([
                "-" * 70,
                f"{domain.name.upper()} (Weight: {domain.weight*100:.0f}%)",
                f"  Domain Maturity: TRL {domain.min_maturity} (min) / {domain.average_maturity:.1f} (avg)",
                f"  Validated: {domain.validated_count}/{len(domain.capabilities)}",
                "",
            ])
            
            for cap in domain.capabilities:
                lines.append(f"  * {cap.to_claim_string()}")
                if cap.gap_description and not cap.validated:
                    lines.append(f"    Gap: {cap.gap_description}")
            lines.append("")
        
        lines.extend([
            "=" * 70,
            "WHAT THIS MEANS",
            "=" * 70,
            "",
            f"TRL {self.bottleneck_maturity} indicates: {MaturityLevel.from_level(max(1, self.bottleneck_maturity)).value}",
            "",
            "To advance to TRL 4 (Lab Validated):",
            "  - Build physical prototype",
            "  - Run component-level tests",
            "  - Document all measurements",
            "",
            "To advance to TRL 6 (Prototype Demonstrated):",
            "  - Integrate all subsystems",
            "  - Test in realistic environment",
            "  - Demonstrate to stakeholders",
            "",
        ])
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Export as dictionary for JSON/YAML serialization."""
        return {
            "system_name": self.system_name,
            "version": self.version,
            "assessment_date": self.assessment_date.isoformat() if self.assessment_date else None,
            "summary": {
                "overall_maturity_trl": self.bottleneck_maturity,
                "weighted_average_trl": round(self.overall_maturity, 1),
                "total_capabilities": self.total_capabilities,
                "validated_capabilities": self.validated_capabilities,
            },
            "domains": [d.to_dict() for d in self.domains],
        }
    
    def save_json(self, path: str) -> None:
        """Save assessment to JSON file."""
        data = self.to_dict()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Capability index saved to {path}")
    
    def save_yaml(self, path: str) -> None:
        """Save assessment to YAML file."""
        data = self.to_dict()
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Capability index saved to {path}")
    
    def update_capability(
        self, 
        domain_name: str, 
        capability_name: str,
        measured_value: Optional[float] = None,
        evidence: Optional[Evidence] = None,
        maturity: Optional[MaturityLevel] = None,
    ) -> bool:
        """
        Update a capability with new measurement or evidence.
        
        Returns True if capability was found and updated.
        """
        for domain in self.domains:
            if domain.name.lower() == domain_name.lower():
                for cap in domain.capabilities:
                    if cap.name.lower() == capability_name.lower():
                        if measured_value is not None:
                            cap.measured_value = measured_value
                        if evidence is not None:
                            cap.evidence = evidence
                        if maturity is not None:
                            cap.maturity = maturity
                        self.assessment_date = datetime.now()
                        return True
        return False


def main():
    """Generate capability report from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate PodX Capability Index Report")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", choices=["text", "json", "yaml"], default="text")
    parser.add_argument("--system", "-s", default="PodX Nano v1", help="System name")
    
    args = parser.parse_args()
    
    pci = PodXCapabilityIndex(system_name=args.system)
    pci.assessment_date = datetime.now()
    
    if args.format == "text":
        report = pci.generate_report()
        if args.output:
            Path(args.output).write_text(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)
    elif args.format == "json":
        if args.output:
            pci.save_json(args.output)
        else:
            print(json.dumps(pci.to_dict(), indent=2))
    elif args.format == "yaml":
        if args.output:
            pci.save_yaml(args.output)
        else:
            print(yaml.dump(pci.to_dict(), default_flow_style=False))


if __name__ == "__main__":
    main()

