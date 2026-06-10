import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class GhappylineRewardCalculator(BaseRewardCalculator):
    """Ghappyline奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            a = identity['a']
            n = identity['n']
            
            # 原题解法逻辑
            processed = [a[i] + i for i in range(n)]
            processed_sorted = sorted(processed)
            
            # 检查是否有相邻重复
            has_duplicate = any(processed_sorted[i] == processed_sorted[i+1] for i in range(n-1))
            
            if has_duplicate:
                return solution.strip() == ":("
            else:
                # 构造正确解
                correct_answer = [processed_sorted[i] - i for i in range(n)]
                user_answer = list(map(int, solution.split()))
                return user_answer == correct_answer
        except Exception:
            return False
    
    # 其他额外方法

