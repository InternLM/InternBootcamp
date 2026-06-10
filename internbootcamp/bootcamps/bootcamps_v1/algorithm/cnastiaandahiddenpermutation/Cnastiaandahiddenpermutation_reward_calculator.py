import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CnastiaandahiddenpermutationRewardCalculator(BaseRewardCalculator):
    """Cnastiaandahiddenpermutation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'!([\d\s]+)', output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = list(map(int, last_match.split()))
        except:
            return None
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['permutation']
    
    # 其他额外方法

