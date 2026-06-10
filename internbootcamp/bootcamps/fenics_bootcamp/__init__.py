# FEniCS Thermal Control Bootcamp Module
from .fenics_reward_calculator import FenicsRewardCalculator
from .ip import ips

# 兼容 bootcamp/ThermalControl -> ThermalControlRewardCalculator 的命名约定
ThermalControlRewardCalculator = FenicsRewardCalculator

__all__ = [
    "FenicsRewardCalculator",
    "ThermalControlRewardCalculator",
    "ips"
]
