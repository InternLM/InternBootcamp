import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 998244353



# === 源文件中的全局函数 ===

def solve(n, c_list):
    C = [x - 1 for x in c_list]
    DP = [[1] * (n + 1) for _ in range(n + 1)]
    for le in range(1, n + 1):
        for i in range(n - le + 1):
            j = i + le
            k = min(range(i, j), key=lambda x: C[x])
            ans1 = 0
            for split in range(i, k + 1):
                ans1 = (ans1 + DP[i][split] * DP[split][k]) % MOD
            ans2 = 0
            for split in range(k + 1, j + 1):
                ans2 = (ans2 + DP[k + 1][split] * DP[split][j]) % MOD
            DP[i][j] = (ans1 * ans2) % MOD
    return DP[0][n] % MOD


class F1shortcolorfulstripRewardCalculator(BaseRewardCalculator):
    """F1shortcolorfulstrip奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        # 移除可能的逗号等非数字字符
        cleaned = last_match.replace(',', '').replace(' ', '')
        try:
            return int(cleaned)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct = identity['correct_answer']
        return solution == correct
    
    # 其他额外方法

