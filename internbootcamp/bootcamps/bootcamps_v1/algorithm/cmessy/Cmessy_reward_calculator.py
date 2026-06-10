import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def is_balanced(s):
    balance = 0
    for char in s:
        if char == '(':
            balance += 1
        else:
            balance -= 1
        if balance < 0:
            return False
    return balance == 0

def count_regular_prefixes(s):
    count = 0
    balance = 0
    for i in range(len(s)):
        char = s[i]
        balance += 1 if char == '(' else -1
        if balance < 0:
            break
        if balance == 0:
            count += 1
    return count

def generate_s_final(n, k):
    if k == 0:
        return ''
    prefix = "()" * (k - 1)
    remaining = n - 2 * (k - 1)
    m = remaining // 2
    suffix = '(' * m + ')' * m
    return prefix + suffix


class CmessyRewardCalculator(BaseRewardCalculator):
    """Cmessy奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        lines = [line.strip() for line in answer_block.split('\n') if line.strip()]
        if not lines:
            return None
        try:
            m = int(lines[0])
        except ValueError:
            return None
        if len(lines) < m + 1:
            return None
        operations = []
        for line in lines[1:m+1]:
            parts = line.split()
            if len(parts) != 2:
                return None
            try:
                l = int(parts[0])
                r = int(parts[1])
                if not (1 <= l <= r):
                    return None
                operations.append((l, r))
            except (ValueError, IndexError):
                return None
        return operations
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        s = identity['s']
        n = identity['n']
        k = identity['k']
        current_s = s
        for l, r in solution:
            if l < 1 or r > n or l > r:
                return False
            l_idx = l - 1
            r_idx = r
            substring = current_s[l_idx:r_idx]
            reversed_sub = substring[::-1]
            current_s = current_s[:l_idx] + reversed_sub + current_s[r_idx:]
        if not is_balanced(current_s):
            return False
        regular_count = count_regular_prefixes(current_s)
        return regular_count == k
    
    # 其他额外方法

