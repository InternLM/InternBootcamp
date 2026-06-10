import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
from collections import defaultdict

# === 源文件中的全局函数 ===

def calculate_answer(s, p):
    m = len(p)
    n = len(s)
    if m == 0 or n < m:
        return 0
    
    # Initialize frequency counter for p
    count_p = defaultdict(int)
    for c in p:
        count_p[c] += 1
    
    # Initialize sliding window parameters
    current_counts = defaultdict(int)
    required = len(count_p)
    formed = 0
    ans = 0
    q_count = 0  # number of '?' in current window
    
    left = 0
    for right in range(n):
        # Add right character
        char = s[right]
        if char == '?':
            q_count += 1
        else:
            current_counts[char] += 1
            if current_counts[char] == count_p.get(char, 0):
                formed += 1
        
        # Maintain window size m
        if right - left + 1 > m:
            # Remove left character
            left_char = s[left]
            if left_char == '?':
                q_count -= 1
            else:
                if current_counts[left_char] == count_p.get(left_char, 0):
                    formed -= 1
                current_counts[left_char] -= 1
            left += 1
        
        # Check window validity when window size is exactly m
        if right - left + 1 == m:
            # Calculate needed characters
            needed = sum(max(0, count_p[c] - current_counts[c]) for c in count_p)
            if needed <= q_count and formed == required:
                ans += 1
    
    return ans


class CanagramsearchRewardCalculator(BaseRewardCalculator):
    """Canagramsearch奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](\d+)', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['_answer']
    
    # 其他额外方法

