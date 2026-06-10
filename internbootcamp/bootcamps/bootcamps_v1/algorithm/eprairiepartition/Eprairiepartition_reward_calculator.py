import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import bisect

# === 源文件中的全局函数 ===

def compute_possible_m(a):
    cnt1 = a.count(1)
    n = len(a)
    a_sorted = sorted(a)
    freq = defaultdict(int)
    for num in a_sorted:
        freq[num] += 1

    def is_possible(m):
        current_freq = freq.copy()

        if current_freq.get(1, 0) < m:
            return False
        current_freq[1] -= m

        last = [1] * m
        current_power = 2
        cnt = m

        while current_freq.get(current_power, 0) > 0 and cnt > 0:
            available = current_freq[current_power]
            take = min(available, cnt)
            current_freq[current_power] -= take
            for i in range(take):
                last[i] = current_power
            cnt = take
            current_power *= 2

        last_sorted = sorted(last)
        remaining = []
        for num, count in sorted(current_freq.items()):
            if count > 0:
                remaining.extend([num] * count)

        for num in remaining:
            required = (num + 1) // 2
            idx = bisect.bisect_left(last_sorted, required)
            if idx >= len(last_sorted):
                return False
            del last_sorted[idx]
            bisect.insort(last_sorted, num)

        return True

    left, right = 0, cnt1 + 1
    while left < right - 1:
        mid = (left + right) // 2
        if is_possible(mid):
            right = mid
        else:
            left = mid
    mi = right

    if mi > cnt1:
        return [-1]
    return list(range(mi, cnt1 + 1))


class EprairiepartitionRewardCalculator(BaseRewardCalculator):
    """Eprairiepartition奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            if last_match == '-1':
                return [-1]
            parts = last_match.split()
            solution = list(map(int, parts))
            if solution == [-1]:
                return solution
            if solution != sorted(solution):
                return None
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct = identity['correct_output']
        return solution == correct
    
    # 其他额外方法

