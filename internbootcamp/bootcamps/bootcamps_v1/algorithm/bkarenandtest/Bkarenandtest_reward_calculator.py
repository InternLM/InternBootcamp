import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, a_list):
    mod = MOD
    a = list(a_list)
    sgn = 1
    current_n = n
    
    while current_n % 4 != 1:
        current_n -= 1
        b = []
        current_sgn = sgn
        for i in range(current_n):
            val = (a[i] + current_sgn * a[i+1]) % mod
            b.append(val)
            current_sgn *= -1
        a = b
        sgn *= -1  # Update the starting sign for the next layer
    
    m = current_n // 2
    max_inv = m if m > 1 else 2
    inv = [0] * (max_inv + 2)
    inv[0] = inv[1] = 1
    for i in range(2, m + 1):
        inv[i] = (mod - mod // i * inv[mod % i]) % mod
    
    p = [0] * current_n
    r = p[0] = 1
    for i in range(m):
        coeff = (m - i) * inv[i + 1] % mod
        r = r * coeff % mod
        p[2 * i + 2] = r
    
    ans = 0
    for i in range(current_n):
        ans = (ans + a[i] * p[i]) % mod
    
    return ans % mod


class BkarenandtestRewardCalculator(BaseRewardCalculator):
    """Bkarenandtest奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        try:
            user_ans = int(solution) % MOD
            user_ans = user_ans + MOD if user_ans < 0 else user_ans
            return user_ans == identity['answer']
        except ValueError:
            return False
    
    # 其他额外方法

