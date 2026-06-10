import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def minimal_representation(s):
    n = len(s)
    if n == 0:
        return ''
    s += s
    i, j, k = 0, 1, 0
    while i < n and j < n and k < n:
        if s[i + k] == s[j + k]:
            k += 1
        else:
            if s[i + k] > s[j + k]:
                i += k + 1
            else:
                j += k + 1
            if i == j:
                j += 1
            k = 0
    min_pos = min(i, j)
    return s[min_pos:min_pos + n]


class EcyclicalquestRewardCalculator(BaseRewardCalculator):
    """Ecyclicalquest奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        numbers = []
        for line in last_match.splitlines():
            stripped = line.strip()
            if stripped:
                try:
                    numbers.append(int(stripped))
                except ValueError:
                    continue
        return numbers if numbers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answers']
    
    # 其他额外方法

