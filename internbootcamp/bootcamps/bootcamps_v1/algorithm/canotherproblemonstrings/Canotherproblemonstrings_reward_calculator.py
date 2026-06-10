import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CanotherproblemonstringsRewardCalculator(BaseRewardCalculator):
    """Canotherproblemonstrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        k = identity['k']
        s = identity['s']
        def compute_answer(k_val, s_str):
            a = [1]
            for c in s_str:
                if c == '0':
                    a[-1] += 1
                else:
                    a.append(1)
            if k_val == 0:
                return sum(n * (n - 1) // 2 for n in a)
            else:
                return sum(a * b for a, b in zip(a, a[k_val:])) if len(a) >= k_val else 0
        correct_answer = compute_answer(k, s)
        return solution == correct_answer
    
    # 其他额外方法

