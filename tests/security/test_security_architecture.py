import unittest
import os
import sys
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from security.zero_trust import ZeroTrustFramework, Role
from security.crypto_engine import CryptoEngine
from security.data_sovereignty import DataSovereignty, DataClassification
from security.threat_protection import ThreatProtection
from compliance.compliance_manager import ComplianceManager

class TestSecurityArchitecture(unittest.TestCase):

    def setUp(self):
        self.zt = ZeroTrustFramework()
        self.ce = CryptoEngine()
        self.ds = DataSovereignty()
        self.tp = ThreatProtection()
        self.cm = ComplianceManager()

    def test_zero_trust_authentication(self):
        """Test Zero Trust Authentication and RBAC"""
        # Create a dummy cert
        with open("test_cert.pem", "w") as f:
            f.write("-----BEGIN CERTIFICATE-----\nMOCK\n-----END CERTIFICATE-----")
        
        try:
            self.assertTrue(self.zt.authenticate_device("test_cert.pem"))
            self.assertTrue(self.zt.verify_mfa("user1", "123456"))
            self.assertTrue(self.zt.authorize_access("user1", Role.ADMIN, "restricted_area"))
            self.assertFalse(self.zt.authorize_access("guest1", Role.GUEST, "restricted_area"))
        finally:
            if os.path.exists("test_cert.pem"):
                time.sleep(0.1)
                try:
                    os.remove("test_cert.pem")
                except PermissionError:
                    pass

    def test_crypto_engine(self):
        """Test Cryptographic Operations"""
        key = os.urandom(32)
        data = b"Secret Message"
        
        # AES-256-GCM
        nonce, ct, tag = self.ce.encrypt_data(data, key)
        decrypted = self.ce.decrypt_data(nonce, ct, tag, key)
        self.assertEqual(data, decrypted)
        
        # Post-Quantum Kyber Mock
        sk, pk = self.ce.generate_kyber_key_pair()
        self.assertTrue(len(pk) > 0)
        ct_pqc, ss = self.ce.encapsulate_key(pk)
        self.assertTrue(len(ct_pqc) > 0)

    def test_data_sovereignty(self):
        """Test Data Sovereignty Controls"""
        tag = self.ds.classify_data({}, "military_comms")
        self.assertEqual(tag, DataClassification.TOP_SECRET)
        
        # Should block Top Secret to Cloud
        allowed = self.ds.check_exfiltration_policy(tag, "cloud_storage")
        self.assertFalse(allowed)
        
        # Should allow Public to Cloud
        public_tag = self.ds.classify_data({}, "infotainment")
        allowed = self.ds.check_exfiltration_policy(public_tag, "cloud_storage")
        self.assertTrue(allowed)

    def test_compliance_manager(self):
        """Test Compliance Checks"""
        status = self.cm.run_compliance_check()
        self.assertTrue(status["FedRAMP_High"])
        self.assertTrue(status["ITAR"])
        report = self.cm.generate_audit_report()
        self.assertIn("COMPLIANCE AUDIT REPORT", report)

    def test_threat_protection(self):
        """Test Threat Detection and Response"""
        # Anomaly Detection
        telemetry = {"cpu_usage": 95.0, "network_throughput": 500.0, "login_attempts": 20}
        anomalies = self.tp.detect_anomalies(telemetry)
        self.assertTrue(len(anomalies) > 0)
        
        # SIEM Correlation
        events = [
            {"type": "LOGIN_FAILURE", "timestamp": time.time()},
            {"type": "HIGH_CPU", "timestamp": time.time()}
        ]
        threats = self.tp.correlate_events(events)
        self.assertTrue(len(threats) > 0)
        
        # EDR
        threat_id = threats[0]["id"]
        self.tp.respond_to_threat(threat_id)
        self.assertEqual(len(self.tp.active_threats), 0)

if __name__ == '__main__':
    unittest.main()
