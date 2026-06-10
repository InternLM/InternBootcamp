import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class Koroperationunicode221eRewardCalculator(BaseRewardCalculator):
    """Koroperationunicode221e奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强正则匹配模式"""
        matches = re.findall(r'\[\[\s*(\d+)\s*\]\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """增强数值范围验证"""
        try:
            sol = int(solution)
            if sol < 1:
                return False
        except (ValueError, TypeError):
            return False
        
        if identity["problem_type"] == "compute":
            a, b = identity["a"], identity["b"]
            return sol == a**2 + b**2
        
        if identity["problem_type"] == "solve_x":
            b_val = identity["b"]
            c_val = identity["c"]
            return sol**2 + b_val**2 == c_val and sol <= identity.get("max_num", 10)
        
        if identity["problem_type"] == "solve_y":
            a_val = identity["a"]
            return a_val**2 + sol**2 == identity["c"] and sol <= identity.get("max_num", 10)
        
        return False
    
    # 其他额外方法

