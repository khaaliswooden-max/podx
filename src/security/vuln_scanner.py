import time
import random
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Vulnerability:
    cve_id: str
    severity: str
    component: str
    description: str
    status: str = "OPEN" # OPEN, PATCHED

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

    def scan_system(self) -> List[Vulnerability]:
        """
        Simulates a system scan.
        """
        print("SCAN: Starting vulnerability scan...")
        # In a real system, this would check versions.
        # Here we just return the known open vulns.
        return [v for v in self.known_vulns if v.status == "OPEN"]

    def remediate_vuln(self, cve_id: str, patch_manager: PatchManager):
        for v in self.known_vulns:
            if v.cve_id == cve_id and v.status == "OPEN":
                if patch_manager.apply_patch(cve_id):
                    v.status = "PATCHED"
                    print(f"REMEDIATION: {cve_id} marked as PATCHED")

class SecurityDashboard:
    """
    Visualizes security posture.
    """
    def __init__(self, scanner: VulnerabilityScanner):
        self.scanner = scanner

    def generate_dashboard(self) -> Dict:
        vulns = self.scanner.known_vulns
        return {
            "timestamp": time.time(),
            "total_vulns": len(vulns),
            "open_vulns": len([v for v in vulns if v.status == "OPEN"]),
            "patched_vulns": len([v for v in vulns if v.status == "PATCHED"]),
            "critical_open": len([v for v in vulns if v.status == "OPEN" and v.severity == "CRITICAL"]),
            "high_open": len([v for v in vulns if v.status == "OPEN" and v.severity == "HIGH"]),
        }
