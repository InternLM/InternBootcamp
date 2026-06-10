import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random

# === 源文件中的全局函数 ===

def solve(n, p_list, x, a, y, b, k):
    arr = sorted(p_list, reverse=True)
    # 确保x是较大值并交换参数
    if y > x:
        x, y = y, x
        a, b = b, a
    
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    g = gcd(a, b)
    lcm_ab = (a * b) // g if g != 0 else 0
    lo = 0
    hi = n
    
    while lo < hi:
        mid = (lo + hi) // 2
        cnt1 = mid // lcm_ab if lcm_ab != 0 else 0
        cnt2 = mid // a - cnt1
        cnt3 = mid // b - cnt1
        
        total = 0
        ind = 0
        # 处理x+y%的贡献
        for _ in range(cnt1):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * (x + y)
            ind += 1
        # 处理x%的贡献
        for _ in range(cnt2):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * x
            ind += 1
        # 处理y%的贡献
        for _ in range(cnt3):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * y
            ind += 1
        
        if total >= k:
            hi = mid
        else:
            lo = mid + 1
    
    return lo if lo <= n else -1  # 移除多余验证


class AsavethenatureRewardCalculator(BaseRewardCalculator):
    """Asavethenature奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = solve(
                identity['n'], identity['p'],
                identity['x'], identity['a'],
                identity['y'], identity['b'],
                identity['k']
            )
            return solution == expected
        except:
            return False
    
    # 其他额外方法

