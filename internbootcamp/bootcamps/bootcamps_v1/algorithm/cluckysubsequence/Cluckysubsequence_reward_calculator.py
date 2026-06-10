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

def calculate_answer(n, k, a):
    rest = 0
    lk = {}

    def islucky(x):
        nonlocal rest
        s = str(x)
        for c in s:
            if c not in {'4', '7'}:
                rest += 1
                return False
        lk[x] = lk.get(x, 0) + 1
        return True

    for elem in a:
        islucky(elem)

    llk = list(lk.values())
    m = len(llk)
    dp = {}

    def solve(ind, need):
        if need == 0:
            return 1
        if ind < 0 or need < 0 or ind + 1 < need:
            return 0
        if (ind, need) in dp:
            return dp[(ind, need)]
        res = (solve(ind-1, need) + solve(ind-1, need-1) * llk[ind]) % MOD
        dp[(ind, need)] = res
        return res

    facts = [1] * (n + 5)
    for i in range(2, len(facts)):
        facts[i] = (facts[i-1] * i) % MOD

    def comber(a_num, b_num):
        if b_num == 0:
            return 1
        if b_num > a_num or a_num < 0 or b_num < 0:
            return 0
        numerator = facts[a_num]
        denominator = (facts[b_num] * facts[a_num - b_num]) % MOD
        return (numerator * pow(denominator, MOD-2, MOD)) % MOD

    ans = 0
    max_i = min(m, k)
    for i in range(0, max_i + 1):
        needed = k - i
        if needed < 0 or needed > rest:
            continue
        way_lucky = solve(m-1, i) if m > 0 else (0 if i > 0 else 1)
        way_non_lucky = comber(rest, needed)
        ans = (ans + way_lucky * way_non_lucky) % MOD
    return ans


class CluckysubsequenceRewardCalculator(BaseRewardCalculator):
    """Cluckysubsequence奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip()) % MOD
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('expected')
        if expected is None:
            return False
        return (solution % MOD) == (expected % MOD)
    
    # 其他额外方法

