import unittest
import time
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from security.soc_platform import SOCPlatform, Severity
from security.vuln_scanner import VulnerabilityScanner, PatchManager, SecurityDashboard

class TestSecurityOps(unittest.TestCase):
    def setUp(self):
        self.soc = SOCPlatform()
        self.scanner = VulnerabilityScanner()
        self.patch_manager = PatchManager()

    def test_soc_brute_force_detection(self):
        print("\nTesting SOC Brute Force Detection...")
        # Simulate 3 failed logins
        ip = "192.168.1.100"
        for _ in range(3):
            self.soc.process_event("auth_server", "failed login", {"ip": ip})
        
        # Check for incident
        incidents = self.soc.engine.incidents
        self.assertTrue(len(incidents) > 0)
        self.assertEqual(incidents[0].severity, Severity.HIGH)
        self.assertIn("Brute force", incidents[0].description)
        
        # Check response
        self.assertIn(ip, self.soc.response.active_blocks)
        print("✓ Brute force detected and IP blocked")

    def test_soc_malware_detection(self):
        print("\nTesting SOC Malware Detection...")
        self.soc.process_event("endpoint", "suspicious process", {"process_id": "evil.exe", "host": "pc1"})
        
        incidents = self.soc.engine.incidents
        malware_incidents = [i for i in incidents if "Malware" in i.description]
        self.assertTrue(len(malware_incidents) > 0)
        self.assertEqual(malware_incidents[0].severity, Severity.CRITICAL)
        self.assertIn("evil.exe", self.soc.response.terminated_processes)
        print("✓ Malware detected and process terminated")

    def test_vuln_scanner_remediation(self):
        print("\nTesting Vulnerability Remediation...")
        initial_vulns = self.scanner.scan_system()
        target_cve = "CVE-2024-0003"
        
        # Verify target is open
        self.assertTrue(any(v.cve_id == target_cve for v in initial_vulns))
        
        # Remediate
        self.scanner.remediate_vuln(target_cve, self.patch_manager)
        
        # Verify patched
        final_vulns = self.scanner.scan_system()
        patched_vuln = next((v for v in self.scanner.known_vulns if v.cve_id == target_cve), None)
        self.assertEqual(patched_vuln.status, "PATCHED")
        print("✓ Vulnerability remediated and verified")

    def test_compliance_report(self):
        print("\nTesting Compliance Reporting...")
        report = self.soc.get_status()
        self.assertIn("Security Compliance Report", report)
        self.assertIn("MTTD", report)
        print("✓ Compliance report generated")

if __name__ == '__main__':
    unittest.main()
