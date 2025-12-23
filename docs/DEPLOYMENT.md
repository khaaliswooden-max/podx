# PodX Deployment Guide

## Overview

This guide covers deployment procedures for PodX Mobile Distributed Data Center, from development environments to full production deployments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Deployment](#development-deployment)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Hardware Configuration](#hardware-configuration)
- [Network Setup](#network-setup)
- [Security Hardening](#security-hardening)
- [Monitoring Setup](#monitoring-setup)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Software Requirements

- **Operating System**: Ubuntu 22.04 LTS or RHEL 8+
- **Python**: 3.11 or later
- **Container Runtime**: Docker 24+ or Podman 4+
- **Orchestration**: Kubernetes 1.28+ (production)

### Hardware Requirements

#### Development
- 16GB RAM minimum
- 100GB disk space
- Internet connectivity

#### Staging
- 64GB RAM
- 500GB SSD storage
- Multi-core CPU (8+ cores)

#### Production (PodX Hardware)
- 4× AMD EPYC 9654 CPUs
- 2TB DDR5 ECC RAM
- 8× NVIDIA L40S GPUs
- 480TB NVMe RAID-6 storage
- 15kW solar array
- 60kWh battery bank

---

## Development Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/khaaliswooden-max/podx.git
cd podx

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Validate environment
python scripts/validate_environment.py

# Run tests
pytest tests/

# Start dashboard
python src/dashboard/xdop_monitor.py
```

### Development Configuration

Key `.env` settings for development:

```bash
PODX_ENV=development
PODX_LOG_LEVEL=DEBUG
SIMULATION_MODE=true
DEBUG_MODE=true
```

---

## Staging Deployment

### Docker Deployment

```bash
# Build image
docker build -t podx:staging .

# Run container
docker run -d \
  --name podx-staging \
  -p 8080:8080 \
  -v podx-data:/data \
  -e PODX_ENV=staging \
  podx:staging
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: podx-staging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: podx
  template:
    metadata:
      labels:
        app: podx
    spec:
      containers:
      - name: podx
        image: podx:staging
        ports:
        - containerPort: 8080
        env:
        - name: PODX_ENV
          value: "staging"
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Hardware inspection completed
- [ ] Network connectivity verified
- [ ] Power systems tested
- [ ] Security hardening applied
- [ ] Backup systems configured
- [ ] Monitoring systems ready
- [ ] XdoP benchmark passed

### Deployment Steps

#### 1. Physical Setup (30 minutes)

1. Position enclosure at deployment site
2. Deploy and align solar array
3. Connect external power (if available)
4. Establish network connectivity
5. Connect environmental sensors

#### 2. System Initialization (15 minutes)

```bash
# Power on sequence
./scripts/power_on_sequence.sh

# Network configuration
./scripts/configure_network.sh --site-config site.yaml

# Security baseline
./scripts/apply_security_baseline.sh

# Health check
python scripts/validate_environment.py --production
```

#### 3. Workload Deployment (Variable)

```bash
# Deploy base services
kubectl apply -f deployment/base/

# Deploy applications
kubectl apply -f deployment/apps/

# Verify deployments
kubectl get pods -A
```

#### 4. Final Validation (30 minutes)

```bash
# Run XdoP benchmark
python tests/benchmark_suite.py --full --report validation.txt

# Verify all systems
python scripts/full_system_check.py

# Generate deployment report
python scripts/generate_deployment_report.py
```

---

## Hardware Configuration

### Compute Module Setup

```bash
# Verify CPU configuration
lscpu

# Check GPU status
nvidia-smi

# Verify memory
free -h

# Check storage
lsblk
```

### RAID Configuration

```bash
# Check RAID status
cat /proc/mdstat

# Verify array health
mdadm --detail /dev/md0
```

### Thermal Management

```bash
# Check sensor readings
sensors

# Verify cooling system
python scripts/check_thermal.py
```

---

## Network Setup

### Multi-Path Configuration

```yaml
# /etc/podx/network.yaml
networks:
  primary:
    type: cellular_5g
    priority: 1
    
  secondary:
    type: starlink
    priority: 2
    
  backup:
    type: lora
    priority: 3
    
  emergency:
    type: hf_radio
    priority: 4
```

### DDIL Configuration

```bash
# Configure DDIL parameters
python scripts/configure_ddil.py \
  --autonomy-hours 24 \
  --cache-size 480TB \
  --sync-interval 300
```

---

## Security Hardening

### Baseline Security

```bash
# Apply security baseline
./scripts/security/apply_baseline.sh

# Configure firewall
./scripts/security/configure_firewall.sh

# Enable encryption
./scripts/security/enable_encryption.sh

# Configure MFA
./scripts/security/setup_mfa.sh
```

### Compliance Verification

```bash
# Run compliance check
python scripts/compliance_check.py --frameworks all

# Generate compliance report
python scripts/generate_compliance_report.py
```

---

## Monitoring Setup

### Dashboard Access

After deployment, access the monitoring dashboard:

- **URL**: http://localhost:8080
- **Default credentials**: Set during deployment

### Alerting Configuration

```yaml
# /etc/podx/alerting.yaml
alerts:
  - name: cpu_temperature
    threshold: 85
    severity: critical
    
  - name: battery_low
    threshold: 20
    severity: warning
    
  - name: storage_full
    threshold: 90
    severity: warning
```

---

## Backup & Recovery

### Automated Backups

```bash
# Configure backup schedule
crontab -e

# Add backup job
0 2 * * * /opt/podx/scripts/backup.sh
```

### Recovery Procedures

```bash
# List available backups
./scripts/list_backups.sh

# Restore from backup
./scripts/restore_backup.sh --backup-id BACKUP_ID
```

---

## Troubleshooting

### Common Issues

#### System Won't Start
1. Check power systems
2. Verify network connectivity
3. Review system logs: `journalctl -u podx`

#### Performance Degradation
1. Check thermal conditions
2. Verify storage health
3. Review resource utilization

#### Network Issues
1. Check all connectivity paths
2. Verify DDIL cache status
3. Review handover logs

### Support

For additional support:
- **Documentation**: `/docs` directory
- **Support Portal**: support@visionblox.com
- **Emergency Hotline**: +1 (256) 555-PODX

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-01 | Initial release |
| 1.1 | 2025-06-01 | Added Kubernetes deployment |
| 1.2 | 2025-12-01 | Updated for Gen 1.5 |


