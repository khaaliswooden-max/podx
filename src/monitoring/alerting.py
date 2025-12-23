"""
Alert Manager
=============

Manages system alerts and notifications.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from threading import Lock

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertState(Enum):
    """Alert lifecycle states."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class Alert:
    """Represents a system alert."""
    id: str
    severity: AlertSeverity
    title: str
    message: str
    source: str
    state: AlertState = AlertState.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Defines conditions for triggering alerts."""
    id: str
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    message_template: str
    cooldown_seconds: float = 300
    enabled: bool = True
    last_triggered: Optional[datetime] = None


class AlertManager:
    """
    Manages system alerts and notifications.
    
    Features:
    - Rule-based alert triggering
    - Alert lifecycle management
    - Notification callbacks
    - Alert history
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize alert manager.
        
        Args:
            max_history: Maximum alerts to keep in history
        """
        self.max_history = max_history
        
        self._rules: Dict[str, AlertRule] = {}
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._lock = Lock()
        self._alert_counter = 0
        
        self._notification_callbacks: List[Callable[[Alert], None]] = []
        
        self._setup_default_rules()
        logger.info("Alert Manager initialized")
    
    def _setup_default_rules(self) -> None:
        """Set up default alerting rules."""
        default_rules = [
            AlertRule(
                id="cpu_temp_critical",
                name="CPU Temperature Critical",
                condition=lambda m: m.get('cpu_temperature_c', 0) > 85,
                severity=AlertSeverity.CRITICAL,
                message_template="CPU temperature exceeded critical threshold: {cpu_temperature_c}°C",
            ),
            AlertRule(
                id="cpu_temp_warning",
                name="CPU Temperature Warning",
                condition=lambda m: 75 < m.get('cpu_temperature_c', 0) <= 85,
                severity=AlertSeverity.WARNING,
                message_template="CPU temperature elevated: {cpu_temperature_c}°C",
            ),
            AlertRule(
                id="battery_critical",
                name="Battery Level Critical",
                condition=lambda m: m.get('battery_charge_pct', 100) < 10,
                severity=AlertSeverity.CRITICAL,
                message_template="Battery level critical: {battery_charge_pct}%",
            ),
            AlertRule(
                id="battery_low",
                name="Battery Level Low",
                condition=lambda m: 10 <= m.get('battery_charge_pct', 100) < 20,
                severity=AlertSeverity.WARNING,
                message_template="Battery level low: {battery_charge_pct}%",
            ),
            AlertRule(
                id="storage_full",
                name="Storage Nearly Full",
                condition=lambda m: m.get('storage_utilization_pct', 0) > 90,
                severity=AlertSeverity.WARNING,
                message_template="Storage utilization high: {storage_utilization_pct}%",
            ),
            AlertRule(
                id="network_down",
                name="All Networks Down",
                condition=lambda m: m.get('active_connections', 1) == 0,
                severity=AlertSeverity.CRITICAL,
                message_template="All network connections lost - entering DDIL mode",
            ),
            AlertRule(
                id="security_threat",
                name="Security Threat Detected",
                condition=lambda m: m.get('threat_level', 'low') in ['high', 'critical'],
                severity=AlertSeverity.EMERGENCY,
                message_template="Security threat detected: {threat_level}",
            ),
        ]
        
        for rule in default_rules:
            self._rules[rule.id] = rule
    
    def evaluate_rules(self, metrics: Dict[str, Any], source: str = "system") -> List[Alert]:
        """
        Evaluate all rules against current metrics.
        
        Args:
            metrics: Current system metrics
            source: Source identifier
            
        Returns:
            List of newly triggered alerts
        """
        new_alerts = []
        
        with self._lock:
            for rule in self._rules.values():
                if not rule.enabled:
                    continue
                
                # Check cooldown
                if rule.last_triggered:
                    elapsed = (datetime.now() - rule.last_triggered).total_seconds()
                    if elapsed < rule.cooldown_seconds:
                        continue
                
                try:
                    if rule.condition(metrics):
                        alert = self._create_alert(rule, metrics, source)
                        new_alerts.append(alert)
                        rule.last_triggered = datetime.now()
                except Exception as e:
                    logger.error(f"Error evaluating rule {rule.id}: {e}")
        
        return new_alerts
    
    def _create_alert(
        self,
        rule: AlertRule,
        metrics: Dict[str, Any],
        source: str
    ) -> Alert:
        """Create a new alert from a rule."""
        self._alert_counter += 1
        alert_id = f"ALT-{self._alert_counter:06d}"
        
        # Format message with metrics
        try:
            message = rule.message_template.format(**metrics)
        except KeyError:
            message = rule.message_template
        
        alert = Alert(
            id=alert_id,
            severity=rule.severity,
            title=rule.name,
            message=message,
            source=source,
            metadata={'rule_id': rule.id, 'metrics': metrics},
        )
        
        self._active_alerts[alert_id] = alert
        self._alert_history.append(alert)
        
        # Trim history
        if len(self._alert_history) > self.max_history:
            self._alert_history = self._alert_history[-self.max_history:]
        
        # Notify callbacks
        for callback in self._notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Notification callback error: {e}")
        
        logger.warning(f"Alert triggered: [{alert.severity.value}] {alert.title} - {alert.message}")
        
        return alert
    
    def create_manual_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        source: str = "manual"
    ) -> Alert:
        """Create a manual alert."""
        with self._lock:
            self._alert_counter += 1
            alert_id = f"ALT-{self._alert_counter:06d}"
            
            alert = Alert(
                id=alert_id,
                severity=severity,
                title=title,
                message=message,
                source=source,
            )
            
            self._active_alerts[alert_id] = alert
            self._alert_history.append(alert)
            
            for callback in self._notification_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Notification callback error: {e}")
            
            return alert
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert."""
        with self._lock:
            if alert_id not in self._active_alerts:
                return False
            
            alert = self._active_alerts[alert_id]
            alert.state = AlertState.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        with self._lock:
            if alert_id not in self._active_alerts:
                return False
            
            alert = self._active_alerts.pop(alert_id)
            alert.state = AlertState.RESOLVED
            alert.resolved_at = datetime.now()
            
            logger.info(f"Alert {alert_id} resolved")
            return True
    
    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get all active alerts, optionally filtered by severity."""
        with self._lock:
            alerts = list(self._active_alerts.values())
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            return sorted(alerts, key=lambda a: a.created_at, reverse=True)
    
    def get_alert_history(
        self,
        limit: int = 100,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get alert history."""
        with self._lock:
            alerts = self._alert_history.copy()
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            return sorted(alerts, key=lambda a: a.created_at, reverse=True)[:limit]
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add a new alerting rule."""
        with self._lock:
            self._rules[rule.id] = rule
            logger.info(f"Added alert rule: {rule.id}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove an alerting rule."""
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                logger.info(f"Removed alert rule: {rule_id}")
                return True
            return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable an alerting rule."""
        with self._lock:
            if rule_id in self._rules:
                self._rules[rule_id].enabled = True
                return True
            return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable an alerting rule."""
        with self._lock:
            if rule_id in self._rules:
                self._rules[rule_id].enabled = False
                return True
            return False
    
    def register_notification_callback(
        self,
        callback: Callable[[Alert], None]
    ) -> None:
        """Register a callback for alert notifications."""
        self._notification_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        with self._lock:
            active = self._active_alerts.values()
            history = self._alert_history
            
            return {
                'active_count': len(active),
                'active_by_severity': {
                    s.value: sum(1 for a in active if a.severity == s)
                    for s in AlertSeverity
                },
                'total_history': len(history),
                'rules_count': len(self._rules),
                'rules_enabled': sum(1 for r in self._rules.values() if r.enabled),
            }


