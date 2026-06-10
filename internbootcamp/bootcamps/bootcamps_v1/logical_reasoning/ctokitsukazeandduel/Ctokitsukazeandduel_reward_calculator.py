import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def validate_case(n, k, s):
    first = [n] * 2
    last = [-1] * 2
    
    for i in range(n):
        a = int(s[i])
        first[a] = min(first[a], i)
        last[a] = max(last[a], i)
    
    # Check immediate win for 0 or 1
    for a in [0, 1]:
        if first[a] <= last[a] and (last[a] - first[a] + 1) <= k:
            return 'tokitsukaze'
    
    # Check draw conditions
    for a in [0, 1]:
        if first[a] > last[a]:
            continue
        
        left_space = first[a]
        right_space = (n-1) - last[a]
        len_a = last[a] - first[a] + 1
        
        if len_a > (k+1) or left_space >= k or right_space >= k:
            return 'once again'
    
    return 'quailty'


class CtokitsukazeandduelRewardCalculator(BaseRewardCalculator):
    """Ctokitsukazeandduel奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL|re.IGNORECASE)
        return matches[-1].strip().lower() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            k = identity['k']
            s = identity['s']
            correct = validate_case(n, k, s)
            return solution == correct.lower()
        except:
            return False
    
    # 其他额外方法

