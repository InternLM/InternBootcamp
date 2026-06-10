import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answer(n, s):
    if '1' not in s:  # 快速返回全0情况
        return 0
    
    r = [0] * n
    g = [[] for _ in range(n + 2)]
    a = [0] * n
    i = n - 1
    while i >= 0:
        if s[i] == '1':
            j = i
            while j >= 0 and s[j] == '1':
                r[j] = i + 1
                j -= 1
            while i > j:
                x = i - j
                if g[x+1]:
                    a[i] = x * (g[x+1][-1] - i) + a[g[x+1][-1]]
                else:
                    a[i] = x * (n - i)
                g[x].append(i)
                i -= 1
        else:
            i -= 1
    ans = 0
    c = 0
    for i in range(n):
        c += 1
        if s[i] == '0':
            continue
        t = r[i]
        b = t - i
        if i == 0 or s[i-1] == '0':
            for j in range(1, b+1):
                if g[j]:
                    g[j].pop()
        u = b * (b + 1) // 2
        if g[b+1]:
            x = g[b+1][-1]
            u += (x - t) * b + a[x]
        else:
            u += (n - t) * b
        ans += c * u
        c = 0
    return ans


class FfruitsequencesRewardCalculator(BaseRewardCalculator):
    """Ffruitsequences奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强匹配模式
        matches = re.findall(
            r'\[answer\][\s\n]*(\d+)[\s\n]*\[/answer\]', 
            output, 
            re.IGNORECASE
        )
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 严格类型检查
        if not isinstance(solution, int):
            return False
        return solution == identity['correct_answer']
    
    # 其他额外方法

