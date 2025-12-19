"""
PodX Dashboard Module
=====================

Web-based monitoring dashboard for XdoP compliance and system status.
"""

from .xdop_monitor import XdoPMonitor, create_app

__all__ = ['XdoPMonitor', 'create_app']

