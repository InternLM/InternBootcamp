import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

mod = 10**9 + 7



# === 源文件中的全局函数 ===

def calculate_gcd_mod(n, x, a_list):
    sum_total = sum(a_list)
    b = [sum_total - ai for ai in a_list]
    vis = [False] * n
    ans = 1
    while True:
        current_min = None
        for i in range(n):
            if not vis[i] and (current_min is None or b[i] < current_min):
                current_min = b[i]
        if current_min is None or current_min == 0:
            break
        ans = ans * pow(x, current_min, mod) % mod
        count = 0
        new_sum = sum_total - current_min
        for i in range(n):
            if not vis[i]:
                b[i] -= current_min
                if b[i] == 0:
                    count += 1
        sum_total = new_sum
        if sum_total <= 0 or count % x != 0:
            break
        else:
            target = count // x
            p = 0
            for i in range(n):
                if not vis[i] and b[i] == 0:
                    if p < target:
                        b[i] = 1
                        p += 1
                    else:
                        vis[i] = True
    return ans % mod


class CprimenumberRewardCalculator(BaseRewardCalculator):
    """Cprimenumber奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            number_str = ''.join(c for c in last_answer if c.isdigit())
            return int(number_str) if number_str else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        return solution == identity['correct_answer']
    
    # 其他额外方法

