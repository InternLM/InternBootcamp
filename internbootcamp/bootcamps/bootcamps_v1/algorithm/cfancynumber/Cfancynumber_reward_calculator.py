import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_beautiful_number(n, k, original_number):
    s = list(original_number)
    c = [0] * 10
    for i in range(n):
        digit = int(s[i])
        c[digit] += 1

    def choosevalue(m):
        nonlocal c, n, k, s
        if c[m] >= k:
            return (0, original_number)
        p = s.copy()
        total_cost = 0
        remain = k - c[m]
        for i in range(1, 10):
            R = m + i
            L = m - i
            # Process R direction (higher digits)
            if R <= 9 and remain > 0:
                for j in range(n):
                    if remain <= 0:
                        break
                    if int(p[j]) == R:
                        p[j] = str(m)
                        total_cost += i
                        remain -= 1
            # Process L direction (lower digits)
            if L >= 0 and remain > 0:
                for j in range(n-1, -1, -1):
                    if remain <= 0:
                        break
                    if int(p[j]) == L:
                        p[j] = str(m)
                        total_cost += i
                        remain -= 1
            if remain <= 0:
                break
        new_number = ''.join(p)
        return (total_cost, new_number)

    best_cost = float('inf')
    best_number = None
    for m in range(10):
        current_cost, current_number = choosevalue(m)
        if current_cost < best_cost:
            best_cost = current_cost
            best_number = current_number
        elif current_cost == best_cost:
            if current_number < best_number:
                best_number = current_number
    return (best_cost, best_number)


class CfancynumberRewardCalculator(BaseRewardCalculator):
    """Cfancynumber奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        return (lines[0], lines[1])
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            user_cost_str, user_number = solution
            user_cost = int(user_cost_str)
        except:
            return False
        
        n = identity['n']
        if len(user_number) != n:
            return False
        
        correct_cost, correct_number = solve_beautiful_number(
            identity['n'],
            identity['k'],
            identity['original_number']
        )
        
        return user_cost == correct_cost and user_number == correct_number
    
    # 其他额外方法

