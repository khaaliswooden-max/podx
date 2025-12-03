import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class Vulnerability:
    cve_id: str
    severity: str
    component: str
    description: str
    status: str = "OPEN" # OPEN, PATCHED
    discovered_at: float = field(default_factory=time.time)

class PatchManager:
    """
    Manages patching of vulnerabilities.
    """
    def __init__(self):
        self.applied_patches: List[str] = []

    def apply_patch(self, cve_id: str) -> bool:
        """
        Simulates applying a patch.
        """
        print(f"PATCH: Applying patch for {cve_id}...")
        time.sleep(0.1) # Simulate work
        self.applied_patches.append(cve_id)
        return True

    def verify_patch(self, cve_id: str) -> bool:
        return cve_id in self.applied_patches

class VulnerabilityScanner:
    """
    Scans system for vulnerabilities.
    """
    def __init__(self):
        self.known_vulns: List[Vulnerability] = []
        # Seed with some dummy data for simulation
        self._seed_vulns()

    def _seed_vulns(self):
        self.known_vulns.append(Vulnerability("CVE-2024-0001", "HIGH", "OpenSSL", "Buffer overflow"))
        self.known_vulns.append(Vulnerability("CVE-2024-0002", "MEDIUM", "Kernel", "Privilege escalation"))
        self.known_vulns.append(Vulnerability("CVE-2024-0003", "CRITICAL", "Apache Struts", "RCE"))

    def scan_system(self, target_ip: str = "localhost") -> List[Vulnerability]:
        """
        Simulates a system scan.
        """
        print(f"SCAN: Starting vulnerability scan on {target_ip}...")
        # In a real system, this would check versions.
        # Here we just return the known open vulns.
        return [v for v in self.known_vulns if v.status == "OPEN"]

    def remediate_vuln(self, cve_id: str, patch_manager: PatchManager):
        for v in self.known_vulns:
            if v.cve_id == cve_id and v.status == "OPEN":
                if patch_manager.apply_patch(cve_id):
                    # Verify
                    if patch_manager.verify_patch(cve_id):
                        v.status = "PATCHED"
                        print(f"REMEDIATION: {cve_id} marked as PATCHED")
                    else:
                        print(f"REMEDIATION: Failed to verify patch for {cve_id}")

class SecurityDashboard:
    """
    Visualizes security posture.
    """
    def __init__(self, scanner: VulnerabilityScanner):
        self.scanner = scanner

    def generate_dashboard(self) -> Dict:
        vulns = self.scanner.known_vulns
        total = len(vulns)
        open_vulns = [v for v in vulns if v.status == "OPEN"]
        
        score = 100
        for v in open_vulns:
            if v.severity == "CRITICAL": score -= 20
            elif v.severity == "HIGH": score -= 10
            elif v.severity == "MEDIUM": score -= 5
            elif v.severity == "LOW": score -= 1
        
        return {
            "timestamp": time.time(),
            "security_score": max(0, score),
            "total_vulns": total,
            "open_vulns": len(open_vulns),
            "patched_vulns": len([v for v in vulns if v.status == "PATCHED"]),
            "critical_open": len([v for v in vulns if v.status == "OPEN" and v.severity == "CRITICAL"]),
            "high_open": len([v for v in vulns if v.status == "OPEN" and v.severity == "HIGH"]),
            "details": [
                {"cve": v.cve_id, "severity": v.severity, "status": v.status} for v in vulns
            ]
        }

if __name__ == "__main__":
    scanner = VulnerabilityScanner()
    pm = PatchManager()
    
    print("Initial Scan:")
    print(scanner.scan_system())
    
    print("\nRemediating CVE-2024-0003...")
    scanner.remediate_vuln("CVE-2024-0003", pm)
    
    print("\nFinal Dashboard:")
    dash = SecurityDashboard(scanner)
    print(json.dumps(dash.generate_dashboard(), indent=2))
