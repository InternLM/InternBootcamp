import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import bisect
from collections import defaultdict




class CsonyaandrobotsRewardCalculator(BaseRewardCalculator):
    """Csonyaandrobots奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['a']
        first_occurrence = {}
        for idx, num in enumerate(a):
            if num not in first_occurrence:
                first_occurrence[num] = idx
        
        last_occurrence = {}
        for idx in reversed(range(len(a))):
            num = a[idx]
            if num not in last_occurrence:
                last_occurrence[num] = idx
        
        last_positions = sorted(last_occurrence.values())
        total = 0
        for p in first_occurrence:
            p_first = first_occurrence[p]
            cnt = len(last_positions) - bisect.bisect_right(last_positions, p_first)
            total += cnt
        
        return solution == total
    
    # 其他额外方法

