import time
import json
from src.security.soc_platform import SOCPlatform
from src.security.vuln_scanner import VulnerabilityScanner, PatchManager, SecurityDashboard

class SecurityTestSuite:
    def __init__(self):
        self.soc = SOCPlatform()
        self.vuln_scanner = VulnerabilityScanner()
        self.patch_manager = PatchManager()
        self.dashboard = SecurityDashboard(self.vuln_scanner)
        self.results = {}

    def test_brute_force_detection(self):
        """
        Simulates a brute force attack and checks for detection.
        """
        print("TEST: Running Brute Force Detection Test...")
        attacker_ip = "192.168.1.100"
        start_time = time.time()
        
        # Simulate 3 failed logins
        for i in range(3):
            self.soc.process_event("AuthServer", "Failed login attempt", {"ip": attacker_ip})
            time.sleep(0.01)
            
        # Check for incident
        detected = False
        detection_time = 0
        for inc in self.soc.engine.incidents:
            if attacker_ip in inc.description:
                detected = True
                detection_time = inc.timestamp - start_time
                break
        
        # Check for response
        blocked = attacker_ip in self.soc.response.active_blocks
        
        self.results["brute_force"] = {
            "detected": detected,
            "detection_time_sec": detection_time,
            "blocked": blocked,
            "mttd_pass": detection_time < (15 * 60) # 15 mins
        }

    def test_vulnerability_management(self):
        """
        Tests scanning and patching workflow.
        """
        print("TEST: Running Vulnerability Management Test...")
        
        # Initial Scan
        initial_vulns = self.soc.reporter.generate_report([]) # Just to check reporter works
        scan_results = self.vuln_scanner.scan_system()
        initial_count = len(scan_results)
        
        # Patching
        if scan_results:
            target_cve = scan_results[0].cve_id
            self.vuln_scanner.remediate_vuln(target_cve, self.patch_manager)
            
        # Rescan
        post_patch_results = self.vuln_scanner.scan_system()
        final_count = len(post_patch_results)
        
        self.results["vuln_mgmt"] = {
            "initial_vulns": initial_count,
            "final_vulns": final_count,
            "patch_verified": final_count < initial_count
        }

    def run_all_tests(self):
        self.test_brute_force_detection()
        self.test_vulnerability_management()
        return self.results

if __name__ == "__main__":
    suite = SecurityTestSuite()
    results = suite.run_all_tests()
    print(json.dumps(results, indent=2))
