import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import sys
import re
import random

# === 源文件中的全局函数 ===

def getnext(index, fre, k, s, flag):
    if sum(fre) > len(s) - index:
        return "ERROR"
    if index == len(s):
        return ""
    cur = ord(s[index]) - 97 if index < len(s) else 0
    if not flag:
        spare = len(s) - index - sum(fre)
        nexts = ""
        if spare % k == 0:
            nexts += 'a' * (spare // k * k)
        for j in range(26):
            if fre[j] > 0:
                nexts += chr(j + 97) * fre[j]
        return nexts
    nexts = "ERROR"
    for j in range(cur, 26):
        new_flag = flag
        if j > cur:
            new_flag = False
        original_j = fre[j]
        fre[j] -= 1
        if fre[j] < 0:
            fre[j] += k
        temp = getnext(index + 1, fre, k, s, new_flag)
        if temp != "ERROR":
            nexts = chr(j + 97) + temp
            fre[j] = original_j
            return nexts
        fre[j] = original_j
    return nexts

def solve(n, k, s):
    if n % k != 0:
        return "-1"
    fre = [0] * 26
    ans = getnext(0, fre, k, s, True)
    return ans if ans != "ERROR" else "-1"


class CkbeautifulstringsRewardCalculator(BaseRewardCalculator):
    """Ckbeautifulstrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        k = identity['k']
        s = identity['s']
        expected = solve(n, k, s)
        return solution == expected
    
    # 其他额外方法

