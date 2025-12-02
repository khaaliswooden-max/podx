import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from reliability.redundancy_manager import RedundancyManager
from reliability.software_resilience import ResilienceLayer
from reliability.hot_swap_manager import HotSwapManager
from reliability.predictive_maintenance import PredictiveMaintenance
from reliability.fmea_engine import FMEAEngine

def main():
    print("=== Reliability Architecture Verification ===\n")

    # 1. Verify Hardware Redundancy
    print("1. Verifying Hardware Redundancy...")
    rm = RedundancyManager()
    status = rm.get_system_status()
    for component, healthy in status.items():
        print(f"  - {component.capitalize()}: {'[PASS]' if healthy else '[FAIL]'}")
    
    if all(status.values()):
        print("  >> Hardware Redundancy: PASS\n")
    else:
        print("  >> Hardware Redundancy: FAIL\n")

    # 2. Verify Software Resilience
    print("2. Verifying Software Resilience...")
    rl = ResilienceLayer()
    k8s = rl.check_k8s_health()
    minio = rl.check_minio_replication()
    checkpoint = rl.perform_checkpoint("test_app", {"data": "test"})
    watchdog = rl.check_watchdog()
    
    print(f"  - K8s Control Plane: {'[PASS]' if k8s else '[FAIL]'}")
    print(f"  - MinIO Replication: {'[PASS]' if minio else '[FAIL]'}")
    print(f"  - Checkpoint: {'[PASS]' if checkpoint else '[FAIL]'}")
    print(f"  - Watchdog: {'[PASS]' if watchdog else '[FAIL]'}")
    
    if k8s and minio and checkpoint and watchdog:
        print("  >> Software Resilience: PASS\n")
    else:
        print("  >> Software Resilience: FAIL\n")

    # 3. Verify Hot-Swap Manager
    print("3. Verifying Hot-Swap System...")
    hsm = HotSwapManager()
    hsm.register_module("mod_1", "compute")
    hsm.assign_workload("mod_1", {"id": "job_1", "priority": "critical"})
    
    # Simulate failure
    print("  - Simulating module failure...")
    hsm.update_health("mod_1", 0.0) # Fail
    
    # Check if workload migrated (in simulation, we just check logs/logic, here we check if it handled it)
    # Since we don't have a second module registered, it should log a critical error but 'handle' the logic flow
    hsm.register_module("mod_2", "compute") # Add backup
    hsm.assign_workload("mod_1", {"id": "job_2", "priority": "critical"}) # Assign another
    hsm.update_health("mod_1", 0.0) # Fail again to trigger migration
    
    if "mod_2" in hsm.workloads and len(hsm.workloads["mod_2"]) > 0:
        print("  - Workload Migration: [PASS]")
        print("  >> Hot-Swap System: PASS\n")
    else:
        print("  - Workload Migration: [FAIL]")
        print("  >> Hot-Swap System: FAIL\n")

    # 4. Verify Predictive Maintenance
    print("4. Verifying Predictive Maintenance...")
    pm = PredictiveMaintenance()
    # Simulate high temp
    pm.ingest_telemetry("sensor_1", {"temperature": 85.0})
    schedule = pm.get_maintenance_schedule()
    
    if len(schedule) > 0 and schedule[0]["component_id"] == "sensor_1":
        print(f"  - Warning Triggered: [PASS]")
        print(f"  - Maintenance Scheduled: [PASS]")
        print("  >> Predictive Maintenance: PASS\n")
    else:
        print("  >> Predictive Maintenance: FAIL\n")

    # 5. Verify FMEA & Availability Target
    print("5. Verifying FMEA & Availability Target...")
    fmea = FMEAEngine()
    success = fmea.validate_target()
    
    if success:
        print("  >> FMEA Validation: PASS (99.99% Achieved)\n")
    else:
        print("  >> FMEA Validation: FAIL\n")

if __name__ == "__main__":
    main()
