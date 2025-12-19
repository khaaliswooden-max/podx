"""
XdoP Certification Manager
==========================

Manages certification documentation and compliance verification for XdoP Level 3.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class CertificationStatus(Enum):
    """Status of certification process."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_AUDIT = "pending_audit"
    CERTIFIED = "certified"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class CertificationRequirement:
    """Individual certification requirement."""
    id: str
    name: str
    description: str
    threshold: Any
    actual_value: Optional[Any] = None
    met: bool = False
    evidence_path: Optional[str] = None
    notes: str = ""


@dataclass
class CertificationRecord:
    """Record of certification status."""
    certification_id: str
    level: str
    status: CertificationStatus
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    wcbi_score: float = 0.0
    requirements: List[CertificationRequirement] = field(default_factory=list)
    audit_reports: List[str] = field(default_factory=list)


class CertificationManager:
    """
    Manages XdoP certification process and documentation.
    
    Handles:
    - Requirement tracking
    - Evidence collection
    - Certification status management
    - Audit preparation
    - Certificate generation
    """
    
    # Level 3 Mission Critical requirements
    LEVEL_3_REQUIREMENTS = [
        {
            'id': 'L3-001',
            'name': 'Overall WCBI Score',
            'description': 'Weighted Composite Benchmark Index must be ≥85',
            'threshold': 85,
        },
        {
            'id': 'L3-002',
            'name': 'Minimum Domain Score',
            'description': 'All domains must score ≥80',
            'threshold': 80,
        },
        {
            'id': 'L3-003',
            'name': 'DDIL Autonomy',
            'description': 'System must operate autonomously for ≥12 hours',
            'threshold': 12,
        },
        {
            'id': 'L3-004',
            'name': 'MIL-STD Compliance',
            'description': 'MIL-STD-810H environmental compliance required',
            'threshold': True,
        },
        {
            'id': 'L3-005',
            'name': 'Independent Audit',
            'description': 'Third-party audit must be completed',
            'threshold': True,
        },
        {
            'id': 'L3-006',
            'name': 'System Availability',
            'description': 'Demonstrated availability ≥99.9%',
            'threshold': 99.9,
        },
        {
            'id': 'L3-007',
            'name': 'Security Compliance',
            'description': 'Minimum 5 security frameworks implemented',
            'threshold': 5,
        },
        {
            'id': 'L3-008',
            'name': 'Renewable Energy',
            'description': 'Off-grid renewable capability ≥70%',
            'threshold': 70,
        },
    ]
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize certification manager.
        
        Args:
            data_dir: Directory for storing certification data
        """
        self.data_dir = Path(data_dir) if data_dir else Path('./data/certification')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_record: Optional[CertificationRecord] = None
        
        logger.info("Certification Manager initialized")
    
    def initialize_certification(self, certification_id: str, level: str = "Level 3") -> CertificationRecord:
        """
        Initialize a new certification process.
        
        Args:
            certification_id: Unique identifier for this certification
            level: Certification level (default: Level 3)
            
        Returns:
            New CertificationRecord
        """
        requirements = [
            CertificationRequirement(
                id=req['id'],
                name=req['name'],
                description=req['description'],
                threshold=req['threshold'],
            )
            for req in self.LEVEL_3_REQUIREMENTS
        ]
        
        record = CertificationRecord(
            certification_id=certification_id,
            level=level,
            status=CertificationStatus.IN_PROGRESS,
            requirements=requirements,
        )
        
        self.current_record = record
        self._save_record(record)
        
        logger.info(f"Initialized certification: {certification_id}")
        return record
    
    def update_requirement(
        self,
        requirement_id: str,
        actual_value: Any,
        evidence_path: Optional[str] = None,
        notes: str = ""
    ) -> bool:
        """
        Update a requirement with actual measured value.
        
        Args:
            requirement_id: ID of requirement to update
            actual_value: Measured/demonstrated value
            evidence_path: Path to supporting evidence
            notes: Additional notes
            
        Returns:
            True if requirement is now met
        """
        if not self.current_record:
            raise ValueError("No active certification record")
        
        for req in self.current_record.requirements:
            if req.id == requirement_id:
                req.actual_value = actual_value
                req.evidence_path = evidence_path
                req.notes = notes
                
                # Evaluate if requirement is met
                if isinstance(req.threshold, bool):
                    req.met = bool(actual_value) == req.threshold
                elif isinstance(req.threshold, (int, float)):
                    req.met = actual_value >= req.threshold
                else:
                    req.met = actual_value == req.threshold
                
                self._save_record(self.current_record)
                logger.info(f"Updated requirement {requirement_id}: {'MET' if req.met else 'NOT MET'}")
                return req.met
        
        raise ValueError(f"Unknown requirement: {requirement_id}")
    
    def evaluate_certification_readiness(self) -> Dict[str, Any]:
        """
        Evaluate if system is ready for certification.
        
        Returns:
            Dictionary with readiness assessment
        """
        if not self.current_record:
            return {'ready': False, 'reason': 'No active certification record'}
        
        met_count = sum(1 for req in self.current_record.requirements if req.met)
        total_count = len(self.current_record.requirements)
        
        unmet_requirements = [
            {'id': req.id, 'name': req.name, 'threshold': req.threshold, 'actual': req.actual_value}
            for req in self.current_record.requirements
            if not req.met
        ]
        
        ready = met_count == total_count
        
        return {
            'ready': ready,
            'requirements_met': met_count,
            'requirements_total': total_count,
            'completion_percentage': (met_count / total_count) * 100,
            'unmet_requirements': unmet_requirements,
            'status': self.current_record.status.value,
        }
    
    def submit_for_audit(self) -> bool:
        """
        Submit certification for independent audit.
        
        Returns:
            True if submission successful
        """
        if not self.current_record:
            raise ValueError("No active certification record")
        
        readiness = self.evaluate_certification_readiness()
        
        if not readiness['ready']:
            logger.warning("Cannot submit for audit: requirements not met")
            return False
        
        self.current_record.status = CertificationStatus.PENDING_AUDIT
        self._save_record(self.current_record)
        
        logger.info(f"Certification {self.current_record.certification_id} submitted for audit")
        return True
    
    def complete_certification(self, wcbi_score: float, audit_report_path: str) -> CertificationRecord:
        """
        Complete certification after successful audit.
        
        Args:
            wcbi_score: Final WCBI score from audit
            audit_report_path: Path to audit report
            
        Returns:
            Updated CertificationRecord
        """
        if not self.current_record:
            raise ValueError("No active certification record")
        
        self.current_record.status = CertificationStatus.CERTIFIED
        self.current_record.wcbi_score = wcbi_score
        self.current_record.issue_date = datetime.now()
        self.current_record.expiry_date = datetime.now() + timedelta(days=730)  # 2 years
        self.current_record.audit_reports.append(audit_report_path)
        
        self._save_record(self.current_record)
        
        logger.info(f"Certification {self.current_record.certification_id} completed with WCBI {wcbi_score}")
        return self.current_record
    
    def generate_certificate(self, output_path: Optional[str] = None) -> str:
        """
        Generate certification certificate document.
        
        Args:
            output_path: Optional path to save certificate
            
        Returns:
            Certificate content as string
        """
        if not self.current_record:
            raise ValueError("No active certification record")
        
        if self.current_record.status != CertificationStatus.CERTIFIED:
            raise ValueError("Certification not complete")
        
        certificate = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    XDOP LEVEL 3 MISSION CRITICAL                             ║
║                         CERTIFICATE OF COMPLIANCE                            ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  This certifies that:                                                        ║
║                                                                              ║
║                        PODX MOBILE DISTRIBUTED DATA CENTER                   ║
║                                                                              ║
║  Has successfully completed all requirements for XdoP Level 3 Mission        ║
║  Critical certification, demonstrating excellence across all seven           ║
║  benchmark domains.                                                          ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Certification ID:    {self.current_record.certification_id:<45}  ║
║  WCBI Score:          {self.current_record.wcbi_score:<45.1f}  ║
║  Issue Date:          {self.current_record.issue_date.strftime('%Y-%m-%d'):<45}  ║
║  Expiry Date:         {self.current_record.expiry_date.strftime('%Y-%m-%d'):<45}  ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Domain Compliance:                                                          ║
║    ✓ Mobility & Network (20%)      ✓ Security & Compliance (12%)            ║
║    ✓ Energy & Power (18%)          ✓ Ruggedization (10%)                    ║
║    ✓ Reliability (17%)             ✓ Sustainability & TCO (8%)              ║
║    ✓ Compute Performance (15%)                                               ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Certified by: XdoP Standards Consortium                                     ║
║  Verification: https://xdop.org/verify/{self.current_record.certification_id:<30}  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        if output_path:
            Path(output_path).write_text(certificate)
            logger.info(f"Certificate saved to {output_path}")
        
        return certificate
    
    def _save_record(self, record: CertificationRecord) -> None:
        """Save certification record to file."""
        filepath = self.data_dir / f"{record.certification_id}.json"
        
        data = {
            'certification_id': record.certification_id,
            'level': record.level,
            'status': record.status.value,
            'issue_date': record.issue_date.isoformat() if record.issue_date else None,
            'expiry_date': record.expiry_date.isoformat() if record.expiry_date else None,
            'wcbi_score': record.wcbi_score,
            'requirements': [
                {
                    'id': req.id,
                    'name': req.name,
                    'description': req.description,
                    'threshold': req.threshold,
                    'actual_value': req.actual_value,
                    'met': req.met,
                    'evidence_path': req.evidence_path,
                    'notes': req.notes,
                }
                for req in record.requirements
            ],
            'audit_reports': record.audit_reports,
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_record(self, certification_id: str) -> CertificationRecord:
        """Load certification record from file."""
        filepath = self.data_dir / f"{certification_id}.json"
        
        with open(filepath) as f:
            data = json.load(f)
        
        requirements = [
            CertificationRequirement(
                id=req['id'],
                name=req['name'],
                description=req['description'],
                threshold=req['threshold'],
                actual_value=req['actual_value'],
                met=req['met'],
                evidence_path=req['evidence_path'],
                notes=req['notes'],
            )
            for req in data['requirements']
        ]
        
        record = CertificationRecord(
            certification_id=data['certification_id'],
            level=data['level'],
            status=CertificationStatus(data['status']),
            issue_date=datetime.fromisoformat(data['issue_date']) if data['issue_date'] else None,
            expiry_date=datetime.fromisoformat(data['expiry_date']) if data['expiry_date'] else None,
            wcbi_score=data['wcbi_score'],
            requirements=requirements,
            audit_reports=data['audit_reports'],
        )
        
        self.current_record = record
        return record

