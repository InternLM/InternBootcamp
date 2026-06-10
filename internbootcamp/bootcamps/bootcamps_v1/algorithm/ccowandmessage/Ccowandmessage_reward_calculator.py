import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class CcowandmessageRewardCalculator(BaseRewardCalculator):
    """Ccowandmessage奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['s']
        
        # Compute expected answer using the reference algorithm
        d = defaultdict(int)
        for c in s:
            d[c] += 1
        
        n = len(s)
        prefix = [[] for _ in range(n+1)]
        prefix[0] = [0] * 26
        for i in range(n):
            prefix[i+1] = list(prefix[i])
            prefix[i+1][ord(s[i]) - 97] += 1
        
        for i in range(n):
            subsum = [prefix[-1][j] - prefix[i+1][j] for j in range(26)]
            current_char = s[i]
            for j in range(26):
                d[current_char + chr(97 + j)] += subsum[j]
        
        expected = max(d.values()) if d else 0
        return isinstance(solution, int) and solution == expected
    
    # 其他额外方法

