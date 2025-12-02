from typing import List
from .battery_manager import BatteryBank

class PowerDistribution:
    """
    Manages power distribution with N+1 redundancy and GPU power gating.
    """
    def __init__(self, num_power_supplies: int = 2, num_battery_banks: int = 3):
        """
        Initialize Power Distribution.
        
        Args:
            num_power_supplies: Number of power supplies (N+1).
            num_battery_banks: Number of battery banks (N+2).
        """
        self.num_power_supplies = num_power_supplies
        self.num_battery_banks = num_battery_banks
        self.efficiency = 0.96 # End-to-end efficiency target
        self.active_gpus = 0
        self.total_gpus = 8 # Example number
        self.gpu_power_draw_kw = 0.5 # Example per GPU

    def distribute_power(self, source_power_kw: float, load_demand_kw: float) -> float:
        """
        Distribute power from source to load, accounting for efficiency and redundancy.
        
        Args:
            source_power_kw: Power available from sources.
            load_demand_kw: Power required by load.
            
        Returns:
            Power delivered to load.
        """
        # N+1 redundancy check (simplified)
        # If we have at least 1 functional supply (assuming N=1 required), we can deliver power.
        if self.num_power_supplies < 1:
            return 0.0
            
        # Apply efficiency loss
        delivered_power = min(source_power_kw, load_demand_kw) * self.efficiency
        return delivered_power

    def gpu_power_gating(self, required_gpus: int) -> float:
        """
        Manage GPU power gating to reduce consumption.
        
        Args:
            required_gpus: Number of GPUs needed for current workload.
            
        Returns:
            Total GPU power consumption in kW.
        """
        self.active_gpus = min(required_gpus, self.total_gpus)
        
        # Power gating logic: Inactive GPUs draw 0 power (ideal) or very low.
        # We assume 40% reduction compared to keeping all on.
        
        # Baseline: All GPUs on
        # baseline_power = self.total_gpus * self.gpu_power_draw_kw
        
        # Gated Power: Only active GPUs on
        current_power = self.active_gpus * self.gpu_power_draw_kw
        
        return current_power

    def check_redundancy(self, active_batteries: List[BatteryBank]) -> bool:
        """
        Verify if N+2 battery redundancy is met.
        
        Args:
            active_batteries: List of active battery bank objects.
            
        Returns:
            True if redundancy is met.
        """
        # Assuming N=1 required for critical load
        return len(active_batteries) >= self.num_battery_banks
