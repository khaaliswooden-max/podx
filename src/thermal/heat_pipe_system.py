import math

class HeatPipe:
    """
    Models a copper/water heat pipe.
    """
    def __init__(self, diameter_mm: float, length_mm: float, thermal_conductivity_w_mk: float = 400.0):
        self.diameter_mm = diameter_mm
        self.length_mm = length_mm
        self.thermal_conductivity = thermal_conductivity_w_mk
        self.cross_sectional_area_m2 = math.pi * ((diameter_mm / 1000.0) / 2) ** 2
        self.thermal_resistance = self._calculate_thermal_resistance()

    def _calculate_thermal_resistance(self) -> float:
        """
        Calculates the thermal resistance of the heat pipe.
        R = L / (k * A)
        Note: Heat pipes are much more efficient than solid copper. 
        We use an effective thermal conductivity multiplier for the phase change.
        """
        effective_conductivity = self.thermal_conductivity * 100  # Approximation for heat pipe efficiency
        length_m = self.length_mm / 1000.0
        return length_m / (effective_conductivity * self.cross_sectional_area_m2)

class VaporChamber:
    """
    Models a vapor chamber for CPU/GPU contact.
    """
    def __init__(self, width_mm: float, height_mm: float, thickness_mm: float):
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.thickness_mm = thickness_mm
        self.contact_area_m2 = (width_mm / 1000.0) * (height_mm / 1000.0)
        # Simplified thermal resistance for a high-performance vapor chamber
        self.thermal_resistance = 0.05  # °C/W

class RadiatorPanel:
    """
    Models an external radiator panel.
    """
    def __init__(self, surface_area_m2: float, emissivity: float = 0.9):
        self.surface_area_m2 = surface_area_m2
        self.emissivity = emissivity

    def calculate_heat_dissipation(self, panel_temp_c: float, ambient_temp_c: float, fan_speed_rpm: float = 0.0) -> float:
        """
        Calculates heat dissipation via radiation and convection (natural or forced).
        """
        # Stefan-Boltzmann Law for Radiation: P = ε * σ * A * (T_obj^4 - T_env^4)
        sigma = 5.67e-8
        t_panel_k = panel_temp_c + 273.15
        t_ambient_k = ambient_temp_c + 273.15
        
        radiation_watts = self.emissivity * sigma * self.surface_area_m2 * (t_panel_k**4 - t_ambient_k**4)
        
        # Convection: P = h * A * ΔT
        # Natural convection h ~ 10. Forced convection h can be 50-150 depending on airflow.
        # Simple model: h = 10 + (fan_speed_rpm / 50.0)
        # Max fan speed 5000 RPM -> h = 10 + 100 = 110 W/m²K
        h_convection = 10.0 + (fan_speed_rpm / 50.0)
        convection_watts = h_convection * self.surface_area_m2 * (panel_temp_c - ambient_temp_c)
        
        return radiation_watts + convection_watts

class CoolingSystem:
    """
    Integrates heat pipes, vapor chambers, and radiators.
    """
    def __init__(self):
        self.heat_pipes = [HeatPipe(8.0, 300.0) for _ in range(48)]
        self.cpu_vapor_chamber = VaporChamber(100.0, 100.0, 5.0)
        self.gpu_vapor_chambers = [VaporChamber(80.0, 80.0, 5.0) for _ in range(8)]
        self.radiator = RadiatorPanel(4.0)

    def calculate_total_thermal_resistance(self) -> float:
        """
        Calculates the aggregate thermal resistance of the system.
        Parallel heat pipes reduce resistance.
        """
        # Resistance of 48 heat pipes in parallel
        if not self.heat_pipes:
            return float('inf')
        
        single_pipe_r = self.heat_pipes[0].thermal_resistance
        heat_pipes_r = single_pipe_r / len(self.heat_pipes)
        
        # Total R = Vapor Chamber + Heat Pipes + Interface Materials (assumed small)
        # We average the vapor chamber resistance contribution
        total_vapor_r = (self.cpu_vapor_chamber.thermal_resistance + 
                         sum(vc.thermal_resistance for vc in self.gpu_vapor_chambers) / 8) / 2
        
        # Target is < 0.8 °C/W. 
        # This is a simplified system level resistance metric.
        return total_vapor_r + heat_pipes_r

    def get_system_status(self) -> dict:
        return {
            "heat_pipes_count": len(self.heat_pipes),
            "radiator_area_m2": self.radiator.surface_area_m2,
            "thermal_resistance_cw": self.calculate_total_thermal_resistance()
        }
