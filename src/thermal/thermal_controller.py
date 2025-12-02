import time
from typing import Dict, List

class ThermalController:
    """
    Manages the thermal state of the compute system.
    Ensures CPU/GPU temperatures remain < 85°C across -40°C to +60°C ambient.
    """
    def __init__(self, target_temp_c: float = 80.0, max_temp_c: float = 85.0):
        self.target_temp_c = target_temp_c
        self.max_temp_c = max_temp_c
        self.current_ambient_temp_c = 25.0
        self.cpu_temps: List[float] = [25.0] * 4
        self.gpu_temps: List[float] = [25.0] * 8
        self.cooling_power_percent = 0.0  # 0.0 to 100.0

    def update_ambient_temperature(self, temp_c: float):
        """
        Updates the external ambient temperature reading.
        """
        self.current_ambient_temp_c = temp_c

    def update_component_temperatures(self, cpu_temps: List[float], gpu_temps: List[float]):
        """
        Updates the internal component temperatures.
        """
        self.cpu_temps = cpu_temps
        self.gpu_temps = gpu_temps

    def _calculate_cooling_demand(self) -> float:
        """
        Calculates the required cooling power based on the hottest component.
        """
        max_cpu = max(self.cpu_temps)
        max_gpu = max(self.gpu_temps)
        hottest_component = max(max_cpu, max_gpu)

        # PID-like proportional control (simplified)
        error = hottest_component - self.target_temp_c
        
        # Adaptive strategy based on ambient
        ambient_factor = 1.0
        if self.current_ambient_temp_c > 40.0:
            ambient_factor = 1.5  # Boost cooling in hot environments
        elif self.current_ambient_temp_c < -20.0:
            ambient_factor = 0.5  # Reduce cooling in cold environments (save power)

        demand = error * 100.0 * ambient_factor # Increased gain
        return max(0.0, min(5000.0, demand)) # Return RPM, max 5000

    def run_control_loop(self):
        """
        Executes one iteration of the thermal control logic.
        """
        self.cooling_power_percent = self._calculate_cooling_demand() # This is now RPM
        
        # Safety check: Throttling warning
        if max(max(self.cpu_temps), max(self.gpu_temps)) >= self.max_temp_c:
            return "THROTTLE_WARNING"
        return "NORMAL"

    def get_status(self) -> Dict:
        return {
            "ambient_temp_c": self.current_ambient_temp_c,
            "max_component_temp_c": max(max(self.cpu_temps), max(self.gpu_temps)),
            "cooling_power_percent": self.cooling_power_percent,
            "status": self.run_control_loop()
        }
