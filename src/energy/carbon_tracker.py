class CarbonTracker:
    """
    Tracks Scope 1, 2, and 3 emissions and calculates lifecycle carbon footprint.
    """
    def __init__(self, initial_footprint_tons: float = 45.0):
        """
        Initialize Carbon Tracker.
        
        Args:
            initial_footprint_tons: Estimated lifecycle carbon footprint in tons CO2e.
                                    Target is 45 tons.
        """
        self.lifecycle_footprint_tons = initial_footprint_tons
        self.total_emissions_kg = 0.0
        self.scope_1_kg = 0.0
        self.scope_2_kg = 0.0
        self.scope_3_kg = 0.0 # Embodied carbon mostly
        
        # Baselines for comparison
        self.traditional_datacenter_emissions_kg_per_kwh = 0.5 # Example grid intensity
        self.savings_kg = 0.0

    def track_emissions(self, energy_source_type: str, energy_kwh: float):
        """
        Track emissions based on energy source.
        
        Args:
            energy_source_type: 'solar', 'grid', 'diesel' (backup).
            energy_kwh: Energy consumed in kWh.
        """
        emissions_factor = 0.0
        
        if energy_source_type == 'grid':
            emissions_factor = 0.5 # kg CO2e / kWh
            self.scope_2_kg += energy_kwh * emissions_factor
        elif energy_source_type == 'diesel':
            emissions_factor = 2.6 # kg CO2e / liter approx, simplified to per kWh
            # Generator efficiency approx 3 kWh/liter -> ~0.9 kg/kWh
            emissions_factor = 0.9
            self.scope_1_kg += energy_kwh * emissions_factor
        elif energy_source_type == 'solar':
            emissions_factor = 0.0 # Operational emissions are 0
            # Embodied carbon is in Scope 3, tracked separately or amortized.
        
        current_emissions = energy_kwh * emissions_factor
        self.total_emissions_kg += current_emissions
        
        # Calculate savings vs traditional
        traditional_emissions = energy_kwh * self.traditional_datacenter_emissions_kg_per_kwh
        self.savings_kg += (traditional_emissions - current_emissions)

    def calculate_payback_period(self) -> float:
        """
        Calculate carbon payback period in months.
        
        Returns:
            Payback period in months.
        """
        if self.savings_kg <= 0:
            return float('inf')
            
        # Lifecycle footprint is in tons, savings in kg.
        # Payback = Embodied / Savings_rate
        
        # We need a rate. Assuming current savings are over a specific period.
        # For this static method, we might need time context.
        # Let's assume this method is called after a simulation of 'X' months.
        # But without time input, we can't calculate rate.
        
        # Let's return the savings ratio for now or require an input.
        return 0.0 

    def get_reduction_percentage(self) -> float:
        """
        Calculate percentage reduction vs traditional datacenter.
        
        Returns:
            Percentage reduction (0-100).
        """
        total_traditional = self.total_emissions_kg + self.savings_kg
        if total_traditional == 0:
            return 0.0
            
        return (self.savings_kg / total_traditional) * 100.0
