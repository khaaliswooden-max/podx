from dataclasses import dataclass
from typing import List

@dataclass
class ComponentSpec:
    name: str
    count: int
    details: dict

class HardwareConfig:
    """
    Defines the hardware configuration for the ruggedized compute system.
    """
    def __init__(self):
        self.cpu = ComponentSpec(
            name="AMD EPYC 9654",
            count=4,
            details={
                "cores_per_cpu": 96,
                "threads_per_cpu": 192,
                "total_threads": 4 * 192,
                "base_clock": "2.4 GHz",
                "boost_clock": "3.7 GHz",
                "tdp": "360W"
            }
        )
        self.gpu = ComponentSpec(
            name="NVIDIA L40S",
            count=8,
            details={
                "memory": "48GB GDDR6",
                "int8_tops": 320,  # Per GPU? No, total is 320 TOPS in request, but L40S is much faster. 
                                   # Request says "320 TOPS total" which seems low for 8x L40S. 
                                   # L40S is ~800 TOPS INT8 *each*. 
                                   # I will assume the request meant 320 TOPS *per* GPU or simply met the requirement easily.
                                   # Actually, let's stick to the request's aggregate numbers as a minimum requirement.
                "fp16_tflops": 160, # Request target
                "fp64_tflops": 40   # Request target
            }
        )
        self.ram = ComponentSpec(
            name="DDR5 ECC",
            count=1, # Logical bank
            details={
                "capacity": "2TB",
                "speed": "4800 MT/s",
                "bandwidth": "6.4 TB/s aggregate" # Theoretical max for 8-channel * 4 sockets
            }
        )
        self.storage = ComponentSpec(
            name="NVMe Gen5 RAID-6",
            count=1, # Logical volume
            details={
                "capacity": "480TB",
                "seq_read": "28 GB/s",
                "random_iops": "8M"
            }
        )
        self.ruggedization = {
            "pcb_coating": "Conformal Coating (Acrylic/Silicone)",
            "shock_mounts": "Solid-state, 40G rated",
            "sealing": "Hermetic Module Sealing",
            "operating_temp_range": "-40C to +60C"
        }

    def get_total_power_budget(self) -> float:
        """
        Estimates total power budget in Watts.
        """
        cpu_power = 4 * 360 # TDP
        gpu_power = 8 * 350 # L40S TDP approx 350W
        other_power = 500 # RAM, Storage, Motherboard overhead
        return cpu_power + gpu_power + other_power

    def get_config_summary(self) -> dict:
        return {
            "cpu": f"{self.cpu.count}x {self.cpu.name}",
            "gpu": f"{self.gpu.count}x {self.gpu.name}",
            "ram": self.ram.details["capacity"],
            "storage": self.storage.details["capacity"],
            "ruggedization": self.ruggedization
        }
