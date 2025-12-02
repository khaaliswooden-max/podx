import math

class DualAxisTracker:
    """
    Simulates a dual-axis solar tracker to optimize energy capture.
    """
    def __init__(self, tracking_efficiency: float = 0.98):
        """
        Initialize the tracker.
        
        Args:
            tracking_efficiency: Efficiency of the tracking mechanism (0.0 to 1.0).
                                 Default 0.98 accounts for minor mechanical/sensor errors.
        """
        self.tracking_efficiency = tracking_efficiency

    def get_efficiency_multiplier(self, sun_elevation_deg: float) -> float:
        """
        Calculate the efficiency multiplier based on sun position.
        For a dual-axis tracker, we assume near-perfect perpendicularity to the sun
        when the sun is above the horizon.
        
        Args:
            sun_elevation_deg: Elevation of the sun in degrees.
            
        Returns:
            Efficiency multiplier (0.0 to 1.0).
        """
        if sun_elevation_deg <= 0:
            return 0.0
        
        # Dual axis tracker keeps panel perpendicular to sun rays.
        # We apply the mechanical tracking efficiency.
        return self.tracking_efficiency


class SolarArray:
    """
    Simulates a multi-junction III-V solar array.
    """
    def __init__(self, capacity_kw: float = 15.0, efficiency: float = 0.30):
        """
        Initialize the solar array.
        
        Args:
            capacity_kw: Rated capacity in kW. Default 15kW.
            efficiency: Panel efficiency. Default 30% for multi-junction III-V.
        """
        self.capacity_kw = capacity_kw
        self.efficiency = efficiency
        self.tracker = DualAxisTracker()
        self.degradation_factor = 1.0

    def apply_degradation(self, years: float, rate_per_year: float = 0.005):
        """
        Apply annual degradation to the panel efficiency.
        
        Args:
            years: Number of years to simulate degradation for.
            rate_per_year: Degradation rate per year (default 0.5%).
        """
        self.degradation_factor = (1.0 - rate_per_year) ** years

    def calculate_generation(self, irradiance_w_m2: float, duration_hours: float, sun_elevation_deg: float) -> float:
        """
        Calculate energy generation for a given period.
        
        Args:
            irradiance_w_m2: Solar irradiance in W/m^2.
            duration_hours: Duration of the period in hours.
            sun_elevation_deg: Sun elevation in degrees.
            
        Returns:
            Energy generated in kWh.
        """
        # Standard Test Conditions (STC) irradiance is 1000 W/m^2
        stc_irradiance = 1000.0
        
        # Tracker optimizes the angle, so we get the full direct normal irradiance (DNI)
        # modified by the tracker's mechanical efficiency.
        tracker_multiplier = self.tracker.get_efficiency_multiplier(sun_elevation_deg)
        
        if tracker_multiplier == 0:
            return 0.0

        # Power = Irradiance * Area * Efficiency
        # But we define capacity at STC. So:
        # Current Output = Capacity * (Current Irradiance / STC Irradiance) * Tracker * Degradation
        
        normalized_irradiance = irradiance_w_m2 / stc_irradiance
        
        power_kw = self.capacity_kw * normalized_irradiance * tracker_multiplier * self.degradation_factor
        
        energy_kwh = power_kw * duration_hours
        return energy_kwh

    def estimate_daily_generation(self, average_peak_sun_hours: float = 5.0) -> float:
        """
        Estimate daily generation based on peak sun hours.
        Useful for quick validation against the 60-75 kWh target.
        
        Args:
            average_peak_sun_hours: Equivalent hours of STC irradiance per day.
            
        Returns:
            Estimated daily energy in kWh.
        """
        # With dual axis tracking, peak sun hours are effectively increased compared to fixed.
        # However, for this simple estimation, we assume the input accounts for tracking gain
        # or we just use the capacity * hours formula.
        
        # A 15kW array * 5 hours = 75 kWh.
        # With 30% efficiency, the capacity is already the output rating.
        # So 15kW is the output at 1000 W/m^2.
        
        return self.capacity_kw * average_peak_sun_hours * self.degradation_factor
