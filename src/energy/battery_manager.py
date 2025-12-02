class BatteryBank:
    """
    Manages a LiFePO4 battery bank for the renewable energy system.
    """
    def __init__(self, capacity_kwh: float = 60.0, max_discharge_kw: float = 20.0):
        """
        Initialize the battery bank.
        
        Args:
            capacity_kwh: Total capacity in kWh. Default 60kWh.
            max_discharge_kw: Maximum discharge rate in kW. Default 20kW.
        """
        self.capacity_kwh = capacity_kwh
        self.current_charge_kwh = capacity_kwh # Start fully charged
        self.max_discharge_kw = max_discharge_kw
        self.cycle_count = 0
        self.temperature_c = 25.0
        self.health_soh = 1.0 # State of Health (0.0 to 1.0)
        
        # Lifecycle parameters
        self.rated_cycles = 10000
        self.end_of_life_capacity_ratio = 0.80

    def discharge(self, load_kw: float, duration_hours: float) -> float:
        """
        Discharge the battery to meet a load.
        
        Args:
            load_kw: Load in kW.
            duration_hours: Duration in hours.
            
        Returns:
            Energy actually provided in kWh.
        """
        # Check thermal limits
        if self.temperature_c > 45.0:
            # Thermal throttling
            load_kw = min(load_kw, self.max_discharge_kw * 0.5)
        
        requested_energy = load_kw * duration_hours
        available_energy = self.current_charge_kwh
        
        provided_energy = min(requested_energy, available_energy)
        
        self.current_charge_kwh -= provided_energy
        
        # Simple thermal model: discharge heats up battery
        self.temperature_c += (provided_energy / self.capacity_kwh) * 5.0 
        
        return provided_energy

    def charge(self, power_kw: float, duration_hours: float) -> float:
        """
        Charge the battery.
        
        Args:
            power_kw: Charging power in kW.
            duration_hours: Duration in hours.
            
        Returns:
            Energy actually stored in kWh.
        """
        # Check thermal limits
        if self.temperature_c > 45.0:
             power_kw = min(power_kw, self.max_discharge_kw * 0.5)

        added_energy = power_kw * duration_hours
        space_available = (self.capacity_kwh * self.health_soh) - self.current_charge_kwh
        
        stored_energy = min(added_energy, space_available)
        
        self.current_charge_kwh += stored_energy
        
        # Simple thermal model: charging heats up battery
        self.temperature_c += (stored_energy / self.capacity_kwh) * 3.0
        
        return stored_energy

    def thermal_regulation(self, cooling_power_kw: float):
        """
        Apply liquid cooling to reduce temperature.
        
        Args:
            cooling_power_kw: Power applied to cooling system.
        """
        # Simplified cooling model
        cooling_effect = cooling_power_kw * 10.0 # degrees per hour per kW (arbitrary constant for sim)
        self.temperature_c = max(20.0, self.temperature_c - cooling_effect)

    def update_cycles(self):
        """
        Update cycle count and health based on usage.
        Should be called periodically (e.g., daily).
        """
        # Simplified: 1 cycle per day if used
        self.cycle_count += 1
        
        # Linear degradation to 80% at 10,000 cycles
        degradation_per_cycle = (1.0 - self.end_of_life_capacity_ratio) / self.rated_cycles
        self.health_soh = max(self.end_of_life_capacity_ratio, 1.0 - (self.cycle_count * degradation_per_cycle))

    def get_runtime_at_load(self, load_kw: float) -> float:
        """
        Calculate remaining runtime at a specific load.
        
        Args:
            load_kw: Load in kW.
            
        Returns:
            Hours of runtime.
        """
        if load_kw <= 0:
            return float('inf')
        return self.current_charge_kwh / load_kw
