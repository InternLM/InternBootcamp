import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BminimizationRewardCalculator(BaseRewardCalculator):
    """Bminimization奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            try:
                return float(last_match)
            except:
                return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        k = identity['k']
        A = identity['A']
        correct = cls.compute_min_sum(n, k, A)
        return solution == correct
    
    # 其他额外方法

