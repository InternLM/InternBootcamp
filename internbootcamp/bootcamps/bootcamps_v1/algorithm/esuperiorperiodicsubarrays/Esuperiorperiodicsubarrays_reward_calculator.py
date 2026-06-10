import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
from collections import defaultdict
import random
import re

# === 源文件中的全局函数 ===

def solve_puzzle(n, a):
    if n == 1:
        return 0  # s必须≥1且<1，无解

    a_extended = a.copy()
    a_extended.extend(a)
    inf = min(a) - 1
    a_extended[-1] = inf  # 保证最后元素最小
    result = 0

    numbers_by_gcd = defaultdict(list)
    for i in range(1, n):
        current_gcd = math.gcd(i, n)
        numbers_by_gcd[current_gcd].append(i)

    for d in numbers_by_gcd:  # 遍历每个可能的gcd值
        if n % d != 0:
            continue
        
        # 计算每个模位的最大值
        m = [-math.inf] * d
        for i in range(n):
            mod = i % d
            if a_extended[i] > m[mod]:
                m[mod] = a_extended[i]
        
        l = 0
        r = 0
        max_r = len(a_extended) - 1  # 防止越界
        while l < n and r <= max_r:
            if a_extended[r] < m[r % d]:
                # 处理当前有效区间
                sorted_s = sorted(numbers_by_gcd[d])
                for s in sorted_s:
                    if s > (r - l):
                        break
                    # 计算有效区间长度
                    start = l
                    end = min(r - s, n - 1)
                    if start <= end:
                        result += end - start + 1
                l = r + 1
                r = l
            else:
                r += 1
    return result


class EsuperiorperiodicsubarraysRewardCalculator(BaseRewardCalculator):
    """Esuperiorperiodicsubarrays奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 匹配最后出现的答案标签
        matches = re.findall(r'\[/?answer\]', output, re.IGNORECASE)
        if len(matches) < 2:
            return None
        
        last_match = re.findall(r'\[answer\][\s]*(\d+)[\s]*\[/answer\]', output, re.IGNORECASE)
        return int(last_match[-1]) if last_match else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

