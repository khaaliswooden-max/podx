import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass, field

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
    severity: str
    description: str
    status: str = "OPEN"
    affected_assets: List[str] = field(default_factory=list)

class LogAggregator:
    """
    Aggregates logs from various sources in real-time.
    """
    def __init__(self):
        self.logs: List[LogEntry] = []

    def ingest_log(self, entry: LogEntry):
        self.logs.append(entry)
        # In a real system, this might push to a queue or DB
        
    def get_recent_logs(self, duration_seconds: float) -> List[LogEntry]:
        cutoff = time.time() - duration_seconds
        return [log for log in self.logs if log.timestamp >= cutoff]

class IncidentResponse:
    """
    Automated incident response actions.
    """
    def __init__(self):
        self.active_blocks: List[str] = []

    def block_ip(self, ip_address: str):
        if ip_address not in self.active_blocks:
            self.active_blocks.append(ip_address)
            print(f"ACTION: Blocked IP {ip_address}")

    def isolate_host(self, host_id: str):
        print(f"ACTION: Isolated host {host_id}")

class CorrelationEngine:
    """
    Correlates logs to detect threats.
    """
    def __init__(self, response_system: IncidentResponse):
        self.response_system = response_system
        self.incidents: List[Incident] = []

    def analyze_logs(self, logs: List[LogEntry]):
        """
        Simple rule-based analysis.
        """
        # Rule 1: Brute Force Detection (3+ failed logins from same IP)
        failed_logins = {}
        for log in logs:
            if "failed login" in log.message.lower():
                ip = log.metadata.get("ip")
                if ip:
                    failed_logins[ip] = failed_logins.get(ip, 0) + 1
        
        for ip, count in failed_logins.items():
            if count >= 3:
                self._create_incident("HIGH", f"Brute force detected from {ip}", [ip])
                self.response_system.block_ip(ip)

    def _create_incident(self, severity: str, description: str, assets: List[str]):
        # Deduplicate simple incidents
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
        self.incidents.append(incident)
        print(f"ALERT: New Incident {incident.id}: {description}")

class ComplianceReporter:
    """
    Generates compliance reports.
    """
    def generate_report(self, incidents: List[Incident]) -> str:
        report = {
            "timestamp": time.time(),
            "total_incidents": len(incidents),
            "open_incidents": len([i for i in incidents if i.status == "OPEN"]),
            "compliance_status": "COMPLIANT" if not any(i.severity == "CRITICAL" and i.status == "OPEN" for i in incidents) else "NON-COMPLIANT"
        }
        return json.dumps(report, indent=2)

class SOCPlatform:
    def __init__(self):
        self.aggregator = LogAggregator()
        self.response = IncidentResponse()
        self.engine = CorrelationEngine(self.response)
        self.reporter = ComplianceReporter()

    def process_event(self, source: str, message: str, metadata: Dict = None):
        entry = LogEntry(time.time(), source, "INFO", message, metadata or {})
        self.aggregator.ingest_log(entry)
        # Real-time analysis of recent window
        self.engine.analyze_logs(self.aggregator.get_recent_logs(60))

    def get_status(self):
        return self.reporter.generate_report(self.engine.incidents)
