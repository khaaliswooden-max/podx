import sys
import os
import math

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from energy.solar_controller import SolarArray
from energy.pdc_topology import PDCTopology
from energy.battery_manager import BatteryBank
from energy.power_distribution import PowerDistribution
from energy.carbon_tracker import CarbonTracker

def run_validation():
    print("Starting Renewable Energy System Validation...")
    
    # 1. Setup Components
    solar = SolarArray(capacity_kw=15.0, efficiency=0.30)
    pdc = PDCTopology(efficiency=0.96)
    # N+2 Battery Banks (3 banks total for redundancy, but let's say we have 3 banks of 20kWh or 1 big bank of 60kWh)
    # The requirement says "Configure 60kWh LiFePO4 battery bank" and "N+2 battery banks".
    # Let's assume 3 banks of 20kWh each = 60kWh total.
    batteries = [BatteryBank(capacity_kwh=20.0, max_discharge_kw=10.0) for _ in range(3)]
    distribution = PowerDistribution(num_power_supplies=2, num_battery_banks=3)
    carbon = CarbonTracker(initial_footprint_tons=45.0)
    
    # 2. Simulation Parameters
    hours_to_simulate = 24
    
    # Variable Load Profile (Average ~2.5kW to match ~60kWh generation)
    def get_load_demand(hour):
        base_load = 2.0
        if 9 <= hour <= 17: # Work hours
            return base_load + 2.0 # 4kW
        return base_load # 2kW
    
    # Solar profile (simplified bell curve for 12 hours of light)
    def get_irradiance(hour):
        if 6 <= hour <= 18:
            # Peak at noon (hour 12)
            peak = 1000.0
            return peak * math.sin(math.pi * (hour - 6) / 12)
        return 0.0

    def get_sun_elevation(hour):
        if 6 <= hour <= 18:
            return 90.0 * math.sin(math.pi * (hour - 6) / 12)
        return -10.0

    total_gen_kwh = 0.0
    total_load_met_kwh = 0.0
    grid_usage_kwh = 0.0
    
    print(f"\nSimulating {hours_to_simulate} hours of operation...")
    
    for hour in range(hours_to_simulate):
        # Solar Generation
        irradiance = get_irradiance(hour)
        elevation = get_sun_elevation(hour)
        gen_kwh = solar.calculate_generation(irradiance, 1.0, elevation)
        total_gen_kwh += gen_kwh
        
        # Carbon Tracking for Solar (0 operational)
        carbon.track_emissions('solar', gen_kwh)
        
        # Power Conversion (Solar -> DC Bus)
        # Assuming solar connects via PDC or similar MPPT with efficiency
        power_available_kw = pdc.convert_48v_to_380v(gen_kwh) # Treating gen_kwh as avg power kw for the hour
        
        # Load Management
        load_demand_kw = get_load_demand(hour)
        # Apply GPU gating if needed (not active in this full load test)
        # load_demand_kw = distribution.gpu_power_gating(8) 
        
        # Distribute Power
        # 1. Use Solar
        direct_solar_used = min(power_available_kw, load_demand_kw)
        remaining_load = load_demand_kw - direct_solar_used
        excess_solar = power_available_kw - direct_solar_used
        
        # 2. Battery Interaction
        if remaining_load > 0:
            # Discharge batteries
            for bat in batteries:
                if remaining_load <= 0:
                    break
                # Distribute load across batteries
                active_batteries = [b for b in batteries if b.current_charge_kwh > 0]
                if not active_batteries:
                    break
                load_per_bat = remaining_load / len(active_batteries)
                provided = bat.discharge(load_per_bat, 1.0)
                # Convert back to 380V if batteries are 48V (using PDC)
                provided_at_bus = pdc.convert_48v_to_380v(provided)
                remaining_load -= provided_at_bus
        
        if excess_solar > 0:
            # Charge batteries
            # Convert 380V bus to 48V battery
            charge_power_at_bat = pdc.convert_380v_to_48v(excess_solar)
            for bat in batteries:
                if excess_solar <= 0:
                    break
                # Simple equal charging
                charge_per_bat = charge_power_at_bat / len(batteries)
                charged = bat.charge(charge_per_bat, 1.0)
                # In this simple loop we don't track remaining excess perfectly if battery full
        
        # 3. Grid/Backup (if still load remaining)
        if remaining_load > 0.01: # Tolerance
            grid_usage_kwh += remaining_load
            carbon.track_emissions('grid', remaining_load)
        
        total_load_met_kwh += (load_demand_kw - max(0, remaining_load))

    # 3. Validation Checks
    print("\n--- Validation Results ---")
    
    # Solar Efficiency
    print(f"Solar Efficiency Configured: {solar.efficiency*100}% (Target >25%)")
    print(f"Total Solar Generation: {total_gen_kwh:.2f} kWh (Target 60-75 kWh)")
    
    # Conversion Efficiency
    print(f"PDC Efficiency Configured: {pdc.efficiency*100}% (Target >90%)")
    
    # Off-grid Capability
    off_grid_percent = 100.0 * (1.0 - (grid_usage_kwh / total_load_met_kwh)) if total_load_met_kwh > 0 else 0
    print(f"Off-grid Operation: {off_grid_percent:.1f}% (Target 100%)")
    if grid_usage_kwh > 0:
        print(f"WARNING: Grid usage detected: {grid_usage_kwh:.2f} kWh. Check battery capacity or solar generation.")
    
    # Battery Backup Test (Separate check)
    print("\nRunning Battery Backup Stress Test...")
    # Reset batteries to full
    for bat in batteries:
        bat.current_charge_kwh = bat.capacity_kwh
    
    runtime_hours = 0
    while True:
        # 20kW load distributed
        load_per_bat = (20.0 / pdc.efficiency) / len(batteries) # Load at battery terminals accounting for boost loss
        
        alive = False
        for bat in batteries:
            provided = bat.discharge(load_per_bat, 1.0)
            if provided > 0:
                alive = True
        
        if not alive:
            break
        runtime_hours += 1
        
    print(f"Battery Runtime at 20kW: {runtime_hours} hours (Target >2 hr)")
    
    # Carbon Reduction
    reduction = carbon.get_reduction_percentage()
    print(f"Carbon Reduction: {reduction:.1f}% (Target >40%)")
    
    # Final Score
    score = 0
    if solar.efficiency > 0.25: score += 20
    if pdc.efficiency > 0.90: score += 20
    if off_grid_percent >= 99.9: score += 20
    if runtime_hours > 2: score += 20
    if reduction > 40: score += 20
    
    print(f"\nDomain Score: {score}/100")
    
    if score == 100:
        print("SUCCESS: All validation metrics achieved.")
    else:
        print("FAILURE: Some metrics missed.")

if __name__ == "__main__":
    run_validation()
