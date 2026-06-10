import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CacookieforyouRewardCalculator(BaseRewardCalculator):
    """Cacookieforyou奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 强化提取逻辑处理换行和空格
        matches = re.findall(r'\[answer\s*](.*?)\[/answer\s*]', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip().lower()
        return 'Yes' if last_answer == 'yes' else 'No' if last_answer == 'no' else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a, b, n, m = identity['a'], identity['b'], identity['n'], identity['m']
        
        # 处理饼干为零的特殊情况
        if a + b == 0:
            return solution == 'No'
        
        # 主验证逻辑
        a_new, b_new = max(a, b), min(a, b)
        total_guest = n + m
        total_cookie = a_new + b_new
        
        valid = (total_guest <= total_cookie) and (m <= b_new)
        expected = 'Yes' if valid else 'No'
        return solution.lower() == expected.lower()
    
    # 其他额外方法

