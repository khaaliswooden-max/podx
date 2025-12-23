#!/usr/bin/env python3
"""
Seed Data Script
================

Populates the database with initial seed data for development and testing.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_database_path() -> Path:
    """Get database path from environment or default."""
    data_dir = os.getenv('PODX_DATA_DIR', './data')
    db_path = os.getenv('DATABASE_PATH', f'{data_dir}/podx.db')
    return Path(db_path)


def seed_benchmark_results(conn: sqlite3.Connection) -> None:
    """Seed benchmark results."""
    cursor = conn.cursor()
    
    domain_scores = json.dumps({
        'mobility_network': 100,
        'energy_power': 100,
        'reliability': 100,
        'compute_performance': 100,
        'security_compliance': 100,
        'ruggedization': 100,
        'sustainability_tco': 100,
    })
    
    cursor.execute('''
        INSERT INTO benchmark_results (wcbi_score, compliance_level, domain_scores, certification_ready)
        VALUES (?, ?, ?, ?)
    ''', (100.0, 'Level 3 Mission Critical', domain_scores, True))
    
    conn.commit()
    print("✓ Seeded benchmark results")


def seed_sample_metrics(conn: sqlite3.Connection) -> None:
    """Seed sample metrics data."""
    cursor = conn.cursor()
    
    metrics = [
        ('cpu_temperature_c', 65.0, 'compute'),
        ('gpu_temperature_c', 72.0, 'compute'),
        ('battery_charge_pct', 85.0, 'energy'),
        ('solar_generation_kw', 12.5, 'energy'),
        ('network_latency_ms', 12.0, 'network'),
        ('storage_utilization_pct', 15.0, 'storage'),
    ]
    
    for metric_name, value, source in metrics:
        cursor.execute('''
            INSERT INTO metrics (metric_name, value, source)
            VALUES (?, ?, ?)
        ''', (metric_name, value, source))
    
    conn.commit()
    print("✓ Seeded sample metrics")


def seed_audit_log(conn: sqlite3.Connection) -> None:
    """Seed audit log entries."""
    cursor = conn.cursor()
    
    entries = [
        ('authentication', 'admin', 'login_success', 'session', 'MFA verified', '127.0.0.1', True),
        ('configuration', 'admin', 'config_update', 'thermal_threshold', 'Changed from 80 to 85', '127.0.0.1', True),
        ('system', 'system', 'startup', 'podx', 'System initialized', None, True),
    ]
    
    for event_type, user, action, resource, details, source_ip, success in entries:
        cursor.execute('''
            INSERT INTO audit_log (event_type, user, action, resource, details, source_ip, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (event_type, user, action, resource, details, source_ip, success))
    
    conn.commit()
    print("✓ Seeded audit log")


def main():
    """Main seed function."""
    print("PodX Seed Data")
    print("=" * 40)
    
    db_path = get_database_path()
    
    if not db_path.exists():
        print("✗ Database does not exist. Run init_database.py first.")
        return 1
    
    try:
        conn = sqlite3.connect(str(db_path))
        
        seed_benchmark_results(conn)
        seed_sample_metrics(conn)
        seed_audit_log(conn)
        
        conn.close()
        print("\n✓ Seed data loaded successfully")
        return 0
        
    except Exception as e:
        print(f"\n✗ Seeding failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())


