class PDCTopology:
    """
    Adapts 48V automotive architecture to 380VDC datacenter standards.
    """
    def __init__(self, efficiency: float = 0.96):
        """
        Initialize the PDC Topology.
        
        Args:
            efficiency: Conversion efficiency. Target 96% (0.96).
        """
        self.efficiency = efficiency
        self.current_load_kw = 0.0
        self.grid_connected = False # Off-grid by default

    def convert_48v_to_380v(self, power_kw: float) -> float:
        """
        Simulate conversion from 48V sources (like some battery modules) to 380VDC bus.
        
        Args:
            power_kw: Input power in kW.
            
        Returns:
            Output power in kW after conversion losses.
        """
        return power_kw * self.efficiency

    def convert_380v_to_48v(self, power_kw: float) -> float:
        """
        Simulate conversion from 380VDC bus to 48V loads/storage.
        
        Args:
            power_kw: Input power in kW.
            
        Returns:
            Output power in kW after conversion losses.
        """
        return power_kw * self.efficiency

    def manage_load(self, requested_load_kw: float, available_power_kw: float) -> float:
        """
        Manage variable load based on available power.
        
        Args:
            requested_load_kw: The load requested by the datacenter.
            available_power_kw: The total power available from sources.
            
        Returns:
            The actual power delivered to the load.
        """
        # In a real system, this would involve load shedding or battery boosting.
        # For simulation, we determine if we can meet the load.
        
        if available_power_kw >= requested_load_kw:
            self.current_load_kw = requested_load_kw
            return requested_load_kw
        else:
            # If we can't meet the load, we deliver what we have (brownout scenario)
            # or we might need to signal for help (not implemented here).
            self.current_load_kw = available_power_kw
            return available_power_kw

    def vehicle_to_grid(self, vehicle_battery_capacity_kwh: float, discharge_rate_kw: float, duration_hours: float) -> float:
        """
        Simulate V2G (Vehicle to Grid) or in this case Vehicle to Datacenter.
        
        Args:
            vehicle_battery_capacity_kwh: Capacity of the connected vehicle.
            discharge_rate_kw: Rate of discharge.
            duration_hours: Duration of discharge.
            
        Returns:
            Energy provided to the DC bus in kWh.
        """
        # Check if vehicle has enough charge (simplified)
        max_energy = vehicle_battery_capacity_kwh
        requested_energy = discharge_rate_kw * duration_hours
        
        actual_energy = min(max_energy, requested_energy)
        
        # Apply conversion efficiency (assuming vehicle is 400V or 800V, needing adaptation to 380VDC)
        # Or if it's 48V based. We use the standard efficiency.
        return actual_energy * self.efficiency
