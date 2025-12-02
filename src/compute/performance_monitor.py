from typing import Dict

class PerformanceMonitor:
    """
    Monitors system performance metrics and tracks degradation.
    """
    def __init__(self):
        # Baseline capabilities
        self.baseline_metrics = {
            "dmips": 150000,
            "cpu_flops_fp64": 8.0, # TFLOPS
            "gpu_tops_int8": 320.0,
            "gpu_flops_fp16": 160.0, # TFLOPS
            "gpu_flops_fp64": 40.0, # TFLOPS
            "memory_bandwidth_tbs": 6.4,
            "storage_seq_read_gbs": 28.0,
            "storage_random_iops": 8000000
        }
        self.current_degradation_percent = 0.0

    def update_metrics(self, temp_c: float) -> Dict[str, float]:
        """
        Simulates current performance based on temperature.
        Real system would read hardware counters.
        """
        # Simulate degradation based on temperature
        # Requirement: <2% degradation across range
        degradation = 0.0
        if temp_c > 50.0:
            degradation = 0.5 * ((temp_c - 50.0) / 10.0) # Up to 0.5% at 60C
        elif temp_c < -30.0:
            degradation = 0.2 * ((-30.0 - temp_c) / 10.0) # Up to 0.2% at -40C
        
        self.current_degradation_percent = degradation
        
        current_metrics = {}
        factor = 1.0 - (degradation / 100.0)
        
        for key, value in self.baseline_metrics.items():
            current_metrics[key] = value * factor
            
        return current_metrics

    def check_health(self) -> str:
        if self.current_degradation_percent > 2.0:
            return "DEGRADED"
        return "HEALTHY"

    def get_report(self) -> Dict:
        return {
            "baseline": self.baseline_metrics,
            "degradation_percent": self.current_degradation_percent,
            "status": self.check_health()
        }
