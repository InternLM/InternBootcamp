import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def generate_palindrome(min_length=1, max_length=50):
    """Generate palindrome with controlled diversity"""
    length = random.randint(min_length, max_length)
    
    # Ensure non-uniform characters for 90% cases
    if random.random() < 0.9:
        chars = []
        while len(chars) < (length + 1)//2:
            c = random.choice('abcdefghijklmnopqrstuvwxyz')
            if not chars or c != chars[-1]:
                chars.append(c)
        
        # Ensure palindrome structure
        return ''.join(chars + chars[:-1][::-1]) if length%2 else ''.join(chars + chars[::-1])
    
    # Generate uniform palindrome for 10% cases
    c = random.choice('abcdefghijklmnopqrstuvwxyz')
    return c * length

def solve_puzzle(s):
    n = len(s)
    if n <= 1:
        return "Impossible"
    
    # Frequency analysis
    freq = defaultdict(int)
    for c in s:
        freq[c] += 1
    
    # Case 1: All characters same
    if len(freq) == 1:
        return "Impossible"
    
    # Case 2: Check for special odd-length cases
    if n % 2 == 1:
        odd_count = sum(1 for cnt in freq.values() if cnt % 2 != 0)
        if odd_count == 1 and len(freq) == 2:
            return "Impossible"
    
    # Try single cut solutions
    original = list(s)
    for i in range(n//2):
        rotated = s[i+1:] + s[:i+1]
        if rotated != s and rotated == rotated[::-1]:
            return 1
    
    # Default case needs 2 cuts
    return 2


class DsashaandonemorenameRewardCalculator(BaseRewardCalculator):
    """Dsashaandonemorename奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        match = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not match:
            return None
        ans = match[-1].strip()
        return int(ans) if ans.isdigit() else "Impossible"
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_answer']
    
    # 其他额外方法

