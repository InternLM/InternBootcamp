import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from functools import lru_cache




class ConebasedarithmeticRewardCalculator(BaseRewardCalculator):
    """Conebasedarithmetic奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        try:
            return int(matches[-1].strip()) if matches else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            instance = cls()  # 创建带预计算数据的实例
            return int(solution) == instance.calculate_min_ones(n)
        except:
            return False
    
    # 其他额外方法

