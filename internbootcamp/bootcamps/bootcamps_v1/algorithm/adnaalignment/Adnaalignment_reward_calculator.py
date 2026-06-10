import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class AdnaalignmentRewardCalculator(BaseRewardCalculator):
    """Adnaalignment奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            user_ans = int(solution.strip())
        except:
            return False
        
        s = identity['s']
        counts = {'A':0, 'C':0, 'G':0, 'T':0}
        for c in s:
            counts[c] += 1
        
        max_freq = max(counts.values())
        num_options = sum(1 for v in counts.values() if v == max_freq)
        correct_ans = pow(num_options, len(s), MOD)
        
        return user_ans == correct_ans
    
    # 其他额外方法

