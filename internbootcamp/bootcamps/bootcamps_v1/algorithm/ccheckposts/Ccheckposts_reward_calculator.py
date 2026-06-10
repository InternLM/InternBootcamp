import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from itertools import combinations
import re




class CcheckpostsRewardCalculator(BaseRewardCalculator):
    """Ccheckposts奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        parts = last_match.split()
        if len(parts) != 2:
            return None
        try:
            int(parts[0]), int(parts[1])
            return f"{parts[0]} {parts[1]}"
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution.split()) != 2:
            return False
        try:
            total, ways = map(int, solution.split())
        except ValueError:
            return False
        
        calc_total = 0
        calc_ways = 1
        MOD = 10**9 +7
        for scc in identity['scc_list']:
            costs = [identity['costs'][n-1] for n in scc]
            min_cost = min(costs)
            cnt = costs.count(min_cost)
            calc_total += min_cost
            calc_ways = (calc_ways * cnt) % MOD
        
        return total == calc_total and calc_ways == (ways % MOD)
    
    # 其他额外方法

