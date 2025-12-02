import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FMEAEngine:
    """
    Failure Mode and Effects Analysis (FMEA) Engine.
    Calculates system availability based on component failure rates and redundancy.
    """

    def __init__(self):
        # Failure rates (lambda) in failures per year
        # Derived from user specs:
        # Compute: 0.01%/yr = 0.0001
        # Storage: 0.1%/yr = 0.001
        # Network: 1%/day -> ~3.65 failures/year (High, but redundant)
        # Battery: 5%/5yr = 1%/yr = 0.01
        # Cooling: 0.05%/yr = 0.0005
        self.failure_rates = {
            "compute": 0.0001,
            "storage": 0.001,
            "network": 3.65, 
            "battery": 0.01,
            "cooling": 0.0005
        }
        
        # Redundancy configurations (k out of n)
        # Compute: N+1 (e.g., 3 needed, 4 total) -> 1 failure tolerated
        # Storage: RAID-6 (survives 2 failures)
        # Network: 4 paths (1 needed) -> 3 failures tolerated
        # Battery: N+2 (2 failures tolerated)
        # Cooling: Dual (1 failure tolerated)
        self.redundancy = {
            "compute": {"n": 4, "k": 3},
            "storage": {"n": 8, "k": 6}, # RAID-6: n-2
            "network": {"n": 4, "k": 1},
            "battery": {"n": 4, "k": 2}, # Assuming 2 needed, 4 total (N+2)
            "cooling": {"n": 2, "k": 1}
        }

    def calculate_component_availability(self, rate: float, mttr_hours: float = 2.0) -> float:
        """
        Calculate single component availability.
        A = MTBF / (MTBF + MTTR)
        MTBF (hours) = 1 / (rate_per_year / 8760)
        """
        if rate == 0: return 1.0
        failures_per_hour = rate / 8760.0
        mtbf = 1.0 / failures_per_hour
        return mtbf / (mtbf + mttr_hours)

    def calculate_system_availability(self) -> float:
        """
        Calculate overall system availability considering redundancy.
        Parallel system availability (redundancy):
        Ap = 1 - (1 - A)^n  (for 1-out-of-n)
        For k-out-of-n, it's more complex (Binomial), but for high availability:
        Approximate by calculating probability of failure of the redundant set.
        """
        
        # 1. Calculate individual availabilities (A)
        # Using MTTR < 2 hours as achieved
        mttr = 2.0 
        
        a_compute = self.calculate_component_availability(self.failure_rates["compute"], mttr)
        a_storage = self.calculate_component_availability(self.failure_rates["storage"], mttr)
        a_network = self.calculate_component_availability(self.failure_rates["network"], mttr)
        a_battery = self.calculate_component_availability(self.failure_rates["battery"], mttr)
        a_cooling = self.calculate_component_availability(self.failure_rates["cooling"], mttr)

        # 2. Calculate Redundant Group Availabilities
        # Probability of System Failure = Sum of Probabilities of failing > (n-k) components
        
        # Compute (Need 3 of 4): Fails if < 3 work (i.e., > 1 fail). P(fail) ~ n * (1-A)^2 (approx for high A)
        # Exact: P(system_success) = P(4 work) + P(3 work)
        # P(k out of n) = C(n,k) * A^k * (1-A)^(n-k)
        
        def prob_k_out_of_n(n, k, p_success):
            import math
            prob = 0.0
            for i in range(k, n + 1):
                comb = math.comb(n, i)
                prob += comb * (p_success ** i) * ((1 - p_success) ** (n - i))
            return prob

        sys_compute = prob_k_out_of_n(4, 3, a_compute)
        sys_storage = prob_k_out_of_n(8, 6, a_storage) # RAID-6
        sys_network = prob_k_out_of_n(4, 1, a_network) # 1 of 4
        sys_battery = prob_k_out_of_n(4, 2, a_battery) # 2 of 4
        sys_cooling = prob_k_out_of_n(2, 1, a_cooling) # 1 of 2

        # 3. Total System Availability (Series of Subsystems)
        total_availability = sys_compute * sys_storage * sys_network * sys_battery * sys_cooling
        
        logger.info(f"System Availability Calculation:")
        logger.info(f"  Compute (N+1): {sys_compute:.9f}")
        logger.info(f"  Storage (RAID-6): {sys_storage:.9f}")
        logger.info(f"  Network (4-path): {sys_network:.9f}")
        logger.info(f"  Battery (N+2): {sys_battery:.9f}")
        logger.info(f"  Cooling (2N): {sys_cooling:.9f}")
        logger.info(f"  TOTAL: {total_availability:.9f}")
        
        return total_availability

    def validate_target(self) -> bool:
        """Validate if system meets 99.99% availability target."""
        availability = self.calculate_system_availability()
        target = 0.9999
        
        downtime_minutes_per_year = (1.0 - availability) * 365 * 24 * 60
        
        logger.info(f"Projected Annual Downtime: {downtime_minutes_per_year:.2f} minutes")
        
        if availability >= target:
            logger.info("SUCCESS: 99.99% Availability Target MET.")
            return True
        else:
            logger.warning("FAILURE: 99.99% Availability Target NOT MET.")
            return False
