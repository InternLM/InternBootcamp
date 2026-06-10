import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class CfoolsandroadsRewardCalculator(BaseRewardCalculator):
    """Cfoolsandroads奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        try:
            numbers = list(map(int, matches[-1].strip().split()))
            return numbers
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != len(identity["edges"]):
            return False
        
        edge_index = {}
        for idx, (u, v) in enumerate(identity["edges"]):
            edge_key = tuple(sorted((u, v)))
            edge_index[edge_key] = idx
        
        counters = [0] * len(identity["edges"])
        for a, b in identity["pairs"]:
            path = cls._find_path(identity["edges"], a, b)
            for u, v in path:
                edge_key = tuple(sorted((u, v)))
                counters[edge_index[edge_key]] += 1
        
        return solution == counters
    
    # 其他额外方法

