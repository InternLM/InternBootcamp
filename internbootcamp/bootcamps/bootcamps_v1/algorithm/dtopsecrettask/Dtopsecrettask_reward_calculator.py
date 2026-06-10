import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_min_loquacity(n, k, s, q):
    adjusted_s = min(s, (n*n)//2 + 10)  # 严格模拟参考代码的调整逻辑
    INF = float('inf')
    
    # 初始化DP数组，使用滚动数组优化
    dp = [[[INF] * (adjusted_s + 1) for _ in range(k+1)] for __ in range(2)]
    dp[0][0][0] = 0  # 初始状态

    for i in range(1, n+1):
        current = i % 2
        prev = 1 - current
        
        # 重置当前层
        for j in range(k+1):
            for t in range(adjusted_s + 1):
                dp[current][j][t] = INF
        
        # 状态转移
        for pref in range(0, min(i-1, k)+1):
            for done in range(adjusted_s + 1):
                if dp[prev][pref][done] == INF:
                    continue
                
                # 情况1：不选当前士兵
                if dp[current][pref][done] > dp[prev][pref][done]:
                    dp[current][pref][done] = dp[prev][pref][done]
                
                # 情况2：选当前士兵
                new_pref = pref + 1
                if new_pref > k:
                    continue
                
                swaps_needed = i - new_pref  # 与参考代码完全一致的计算方式
                new_done = done + swaps_needed
                
                if new_done <= adjusted_s:
                    new_value = dp[prev][pref][done] + q[i-1]
                    if new_value < dp[current][new_pref][new_done]:
                        dp[current][new_pref][new_done] = new_value
        
    # 寻找最终答案
    final_layer = n % 2
    return min(dp[final_layer][k][:adjusted_s+1])


class DtopsecrettaskRewardCalculator(BaseRewardCalculator):
    """Dtopsecrettask奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected']
    
    # 其他额外方法

