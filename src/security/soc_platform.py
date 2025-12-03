import time
import json
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    timestamp: float
    source: str
    level: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Incident:
    id: str
    timestamp: float
    severity: Severity
    description: str
    status: str = "OPEN"
    affected_assets: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)

class LogAggregator:
    """
    Aggregates logs from various sources in real-time.
    """
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.sources: List[str] = ["firewall", "auth_server", "app_server", "database"]

    def ingest_log(self, entry: LogEntry):
        self.logs.append(entry)
        # Keep only last 10000 logs in memory for simulation
        if len(self.logs) > 10000:
            self.logs = self.logs[-10000:]
        
    def get_recent_logs(self, duration_seconds: float) -> List[LogEntry]:
        cutoff = time.time() - duration_seconds
        return [log for log in self.logs if log.timestamp >= cutoff]

    def simulate_log_stream(self, count: int = 1):
        """Generates random logs for testing."""
        for _ in range(count):
            source = random.choice(self.sources)
            level = random.choice(["INFO", "WARNING", "ERROR"])
            msg = f"Simulated event from {source}"
            meta = {"ip": f"192.168.1.{random.randint(1, 255)}"}
            self.ingest_log(LogEntry(time.time(), source, level, msg, meta))

class IncidentResponse:
    """
    Automated incident response actions.
    """
    def __init__(self):
        self.active_blocks: List[str] = []
        self.quarantined_users: List[str] = []
        self.terminated_processes: List[str] = []

    def execute_response(self, action: str, target: str) -> str:
        if action == "block_ip":
            return self.block_ip(target)
        elif action == "quarantine_user":
            return self.quarantine_user(target)
        elif action == "terminate_process":
            return self.terminate_process(target)
        elif action == "trigger_backup":
            return self.trigger_backup(target)
        else:
            return f"Unknown action: {action}"

    def block_ip(self, ip_address: str) -> str:
        if ip_address not in self.active_blocks:
            self.active_blocks.append(ip_address)
            return f"ACTION: Blocked IP {ip_address}"
        return f"ACTION: IP {ip_address} already blocked"

    def quarantine_user(self, user_id: str) -> str:
        if user_id not in self.quarantined_users:
            self.quarantined_users.append(user_id)
            return f"ACTION: Quarantined user {user_id}"
        return f"ACTION: User {user_id} already quarantined"

    def terminate_process(self, process_id: str) -> str:
        self.terminated_processes.append(process_id)
        return f"ACTION: Terminated process {process_id}"

    def trigger_backup(self, asset_id: str) -> str:
        return f"ACTION: Triggered emergency backup for {asset_id}"

class CorrelationEngine:
    """
    Correlates logs to detect threats using rule-based logic.
    """
    def __init__(self, response_system: IncidentResponse):
        self.response_system = response_system
        self.incidents: List[Incident] = []

    def analyze_logs(self, logs: List[LogEntry]):
        """
        Analyzes a batch of logs for threat patterns.
        """
        self._detect_brute_force(logs)
        self._detect_malware_activity(logs)
        self._detect_data_exfiltration(logs)
        self._detect_privilege_escalation(logs)

    def _detect_brute_force(self, logs: List[LogEntry]):
        failed_logins = {}
        for log in logs:
            if "failed login" in log.message.lower():
                ip = log.metadata.get("ip")
                if ip:
                    failed_logins[ip] = failed_logins.get(ip, 0) + 1
        
        for ip, count in failed_logins.items():
            if count >= 3:
                self._create_incident(
                    Severity.HIGH, 
                    f"Brute force detected from {ip}", 
                    [ip],
                    "block_ip",
                    ip
                )

    def _detect_malware_activity(self, logs: List[LogEntry]):
        for log in logs:
            if "suspicious process" in log.message.lower():
                proc_id = log.metadata.get("process_id")
                host = log.metadata.get("host")
                if proc_id:
                    self._create_incident(
                        Severity.CRITICAL,
                        f"Malware activity detected: {proc_id} on {host}",
                        [host],
                        "terminate_process",
                        proc_id
                    )

    def _detect_data_exfiltration(self, logs: List[LogEntry]):
        # Simplified logic: look for large data transfer logs
        for log in logs:
            if "large data transfer" in log.message.lower():
                user = log.metadata.get("user")
                ip = log.metadata.get("ip")
                self._create_incident(
                    Severity.HIGH,
                    f"Potential data exfiltration by {user} to {ip}",
                    [ip],
                    "quarantine_user",
                    user
                )

    def _detect_privilege_escalation(self, logs: List[LogEntry]):
        for log in logs:
            if "sudo usage" in log.message.lower() and log.level == "WARNING":
                user = log.metadata.get("user")
                self._create_incident(
                    Severity.MEDIUM,
                    f"Suspicious privilege escalation by {user}",
                    [user],
                    "quarantine_user",
                    user
                )

    def _create_incident(self, severity: Severity, description: str, assets: List[str], response_action: str = None, action_target: str = None):
        # Deduplicate open incidents
        for inc in self.incidents:
            if inc.description == description and inc.status == "OPEN":
                return
        
        incident = Incident(
            id=f"INC-{len(self.incidents)+1}",
            timestamp=time.time(),
            severity=severity,
            description=description,
            affected_assets=assets
        )
        
        if response_action and action_target:
            result = self.response_system.execute_response(response_action, action_target)
            incident.actions_taken.append(result)
            
        self.incidents.append(incident)
        print(f"ALERT: New Incident {incident.id} [{severity.value}]: {description}")
        if incident.actions_taken:
            print(f"  -> Response: {incident.actions_taken[-1]}")

class ComplianceReporter:
    """
    Generates compliance reports.
    """
    def generate_report(self, incidents: List[Incident]) -> str:
        total = len(incidents)
        open_incidents = [i for i in incidents if i.status == "OPEN"]
        critical = [i for i in incidents if i.severity == Severity.CRITICAL]
        
        # Calculate Mean Time To Detect (MTTD) - Simulated
        # In a real system, we'd compare log timestamp vs incident timestamp
        mttd = 0.0
        if total > 0:
            # Mock calculation: assume 2 minutes avg for simulation
            mttd = 120.0 

        report = f"""
# Security Compliance Report
Generated at: {time.ctime()}

## Summary
- **Total Incidents**: {total}
- **Open Incidents**: {len(open_incidents)}
- **Critical Incidents**: {len(critical)}
- **Compliance Status**: {"NON-COMPLIANT" if open_incidents else "COMPLIANT"}
- **Mean Time To Detect (MTTD)**: {mttd / 60:.2f} minutes (Target: <15 mins)

## Incident Details
"""
        for inc in incidents[-5:]: # Show last 5
            report += f"- [{inc.id}] {inc.timestamp}: {inc.description} ({inc.severity.value}) - Status: {inc.status}\n"
            
        return report

class SOCPlatform:
    def __init__(self):
        self.aggregator = LogAggregator()
        self.response = IncidentResponse()
        self.engine = CorrelationEngine(self.response)
        self.reporter = ComplianceReporter()

    def process_event(self, source: str, message: str, metadata: Dict = None):
        entry = LogEntry(time.time(), source, "INFO", message, metadata or {})
        self.aggregator.ingest_log(entry)
        # Real-time analysis of recent window (e.g., last 60 seconds)
        self.engine.analyze_logs(self.aggregator.get_recent_logs(60))

    def get_status(self):
        return self.reporter.generate_report(self.engine.incidents)

if __name__ == "__main__":
    # Simple test run
    soc = SOCPlatform()
    print("SOC Platform Initialized")
    
    # Simulate a brute force attack
    print("\n--- Simulating Brute Force ---")
    for _ in range(4):
        soc.process_event("auth_server", "failed login attempt", {"ip": "10.0.0.5"})
        time.sleep(0.1)
        
    # Simulate malware
    print("\n--- Simulating Malware ---")
    soc.process_event("endpoint_agent", "suspicious process started", {"process_id": "malware.exe", "host": "workstation-01"})
    
    print("\n--- Generating Report ---")
    print(soc.get_status())
