import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CdnaalignmentRewardCalculator(BaseRewardCalculator):
    """Cdnaalignment奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 支持标签大小写混合匹配并提取最后出现的答案
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        
        # 提取最后一个答案并处理非数字字符
        last_match = matches[-1].strip()
        digits = ''.join(filter(str.isdigit, last_match))
        if not digits:
            return None
        
        try:
            return int(digits) % (10**9 + 7)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        s = identity['s']
        counts = {
            'A': s.count('A'),
            'C': s.count('C'),
            'G': s.count('G'),
            'T': s.count('T')
        }
        max_count = max(counts.values())
        k = sum(1 for cnt in counts.values() if cnt == max_count)
        mod = 10**9 + 7
        correct_answer = pow(k, n, mod)
        return solution == correct_answer
    
    # 其他额外方法

