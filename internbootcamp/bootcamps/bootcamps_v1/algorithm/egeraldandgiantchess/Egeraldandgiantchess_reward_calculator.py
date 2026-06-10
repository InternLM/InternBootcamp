import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re

# === 源文件中的全局变量 ===

global_fac = [1]

global_inv = [1]

mod_value = 10**9 + 7



# === 源文件中的全局函数 ===

def init_global_fac_inv(maxn):
    global global_fac, global_inv, mod_value
    if maxn < len(global_fac):
        return
    current_len = len(global_fac)
    for i in range(current_len, maxn + 1):
        global_fac.append((global_fac[-1] * i) % mod_value)
        inv_i = pow(i, mod_value - 2, mod_value)
        new_inv = (global_inv[-1] * inv_i) % mod_value
        global_inv.append(new_inv)

def culC(a, b):
    if a < 0 or b < 0 or a < b:
        return 0
    init_global_fac_inv(a)
    return global_fac[a] * global_inv[b] % mod_value * global_inv[a - b] % mod_value

def path(sx, sy, tx, ty):
    dx = tx - sx
    dy = ty - sy
    if dx < 0 or dy < 0:
        return 0
    return culC(dx + dy, dx)

def compute_solution(h, w, blocks):
    mod = 10**9 + 7
    blocks_sorted = sorted(blocks, key=lambda x: (x[0], x[1]))
    blocks_sorted.append((h, w))
    n = len(blocks_sorted)
    dp = [0] * n

    for i in range(n):
        r, c = blocks_sorted[i]
        total = path(1, 1, r, c)
        for j in range(i):
            pr, pc = blocks_sorted[j]
            if pr <= r and pc <= c:
                ways = path(pr, pc, r, c) * dp[j]
                total = (total - ways) % mod
        dp[i] = total % mod
    return dp[-1]


class EgeraldandgiantchessRewardCalculator(BaseRewardCalculator):
    """Egeraldandgiantchess奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

