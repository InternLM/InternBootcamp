import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BthechildandsetRewardCalculator(BaseRewardCalculator):
    """Bthechildandset奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        match = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not match:
            return None
        content = match[-1].strip()
        if content == '-1':
            return -1
        try:
            parts = list(map(int, content.split()))
            if len(parts) < 1:
                return None
            n = parts[0]
            elements = parts[1:1+n]
            if len(elements) != n:
                return None
            return elements
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 验证时优先使用隐藏解信息
        if '_solution' in identity:
            if identity['_solution'] is None:
                return solution == -1
            if solution == -1:
                return False
            return set(solution) == set(identity['_solution'])
        
        # 常规验证逻辑
        if solution == -1:
            return not cls.find_solution(identity['sum'], identity['limit'])
        
        sum_total = 0
        limit = identity['limit']
        seen = set()
        for num in solution:
            if not (1 <= num <= limit) or num in seen:
                return False
            seen.add(num)
            sum_total += num & -num
        return sum_total == identity['sum']
    
    # 其他额外方法

