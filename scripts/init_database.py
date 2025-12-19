#!/usr/bin/env python3
"""
Database Initialization Script
==============================

Initializes the PodX database schema and creates required tables.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_database_path() -> Path:
    """Get database path from environment or default."""
    data_dir = os.getenv('PODX_DATA_DIR', './data')
    db_path = os.getenv('DATABASE_PATH', f'{data_dir}/podx.db')
    return Path(db_path)


def create_schema(conn: sqlite3.Connection) -> None:
    """Create database schema."""
    cursor = conn.cursor()
    
    # Metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            tags TEXT,
            source TEXT
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id TEXT UNIQUE NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT,
            source TEXT,
            state TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            acknowledged_at DATETIME,
            resolved_at DATETIME,
            acknowledged_by TEXT
        )
    ''')
    
    # Benchmark results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benchmark_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            wcbi_score REAL NOT NULL,
            compliance_level TEXT,
            domain_scores TEXT,
            certification_ready BOOLEAN,
            report_path TEXT
        )
    ''')
    
    # Configuration history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            key TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_by TEXT
        )
    ''')
    
    # Audit log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            user TEXT,
            action TEXT NOT NULL,
            resource TEXT,
            details TEXT,
            source_ip TEXT,
            success BOOLEAN
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_state ON alerts(state)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)')
    
    conn.commit()
    print("✓ Database schema created successfully")


def main():
    """Main initialization function."""
    print("PodX Database Initialization")
    print("=" * 40)
    
    db_path = get_database_path()
    
    # Create data directory if needed
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Database path: {db_path}")
    
    # Check if database exists
    if db_path.exists():
        print("Database already exists. Updating schema...")
    else:
        print("Creating new database...")
    
    # Connect and create schema
    try:
        conn = sqlite3.connect(str(db_path))
        create_schema(conn)
        conn.close()
        print("\n✓ Database initialization complete")
        return 0
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

