import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random
import re




class CdashaandpasswordRewardCalculator(BaseRewardCalculator):
    """Cdashaandpassword奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        严格匹配最后一个[answer]标签内的整数
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        精确计算最小操作步数的验证逻辑
        """
        n, m = identity["n"], identity["m"]
        strings = identity["strings"]
        
        # 预计算每个字符串的最短移动距离
        num_dists = [math.inf] * n
        alpha_dists = [math.inf] * n
        special_dists = [math.inf] * n
        
        for i, s in enumerate(strings):
            for pos in range(m):
                # 计算从初始位置(0 index)到pos的移动步数
                move_cost = min(pos, m - pos)
                char = s[pos]
                if char.isdigit():
                    num_dists[i] = min(num_dists[i], move_cost)
                elif char.islower():
                    alpha_dists[i] = min(alpha_dists[i], move_cost)
                elif char in {'#', '*', '&'}:
                    special_dists[i] = min(special_dists[i], move_cost)
        
        # 遍历所有三元组组合
        min_operations = math.inf
        for i in range(n):
            for j in range(n):
                if j == i:
                    continue
                for k in range(n):
                    if k == i or k == j:
                        continue
                    total = num_dists[i] + alpha_dists[j] + special_dists[k]
                    min_operations = min(min_operations, total)
        
        return solution == min_operations
    
    # 其他额外方法

