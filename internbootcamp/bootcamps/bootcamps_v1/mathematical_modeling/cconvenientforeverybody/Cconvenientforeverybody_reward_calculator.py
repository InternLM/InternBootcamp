import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class CconvenientforeverybodyRewardCalculator(BaseRewardCalculator):
    """Cconvenientforeverybody奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强正则表达式鲁棒性
        matches = re.findall(r'\[answer\s*\](\d+)\s*\[/answer\s*\]', output, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        a = identity['a']
        s = identity['s']
        f = identity['f']
        window_size = f - s
        
        # 滑动窗口算法优化
        current_sum = sum(a[:window_size])
        max_sum = current_sum
        candidates = deque([0])
        
        for i in range(1, n):
            current_sum += a[(i + window_size - 1) % n] - a[i-1]
            if current_sum > max_sum:
                max_sum = current_sum
                candidates.clear()
                candidates.append(i)
            elif current_sum == max_sum:
                candidates.append(i)
        
        # 计算所有候选解对应的起始时间
        min_start = n
        for i in candidates:
            mod_value = (s - (i + 1)) % n
            start_time = mod_value + 1 if mod_value != 0 else n  # 修正边界条件
            if start_time < min_start:
                min_start = start_time
        
        return solution == min_start
    
    # 其他额外方法

