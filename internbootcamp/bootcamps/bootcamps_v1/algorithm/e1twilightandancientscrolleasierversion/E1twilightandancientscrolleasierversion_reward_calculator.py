import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
import bisect

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, words):
    if n == 0:
        return 0
    preprocessed = []
    for s in words:
        m = len(s)
        deletions = [s[:i] + s[i+1:] for i in range(m)]
        deletions.sort()
        preprocessed.append(deletions)
    
    prev_deletions = preprocessed[0]
    prev_prefix_sum = [0] * (len(prev_deletions) + 1)
    for i in range(len(prev_deletions)):
        prev_prefix_sum[i+1] = (prev_prefix_sum[i] + 1) % MOD
    
    for x in range(1, n):
        current_deletions = preprocessed[x]
        current_dp = []
        for s in current_deletions:
            j = bisect.bisect_right(prev_deletions, s)
            current_count = prev_prefix_sum[j]
            current_dp.append(current_count % MOD)
        
        current_prefix_sum = [0]
        current_sum = 0
        for cnt in current_dp:
            current_sum = (current_sum + cnt) % MOD
            current_prefix_sum.append(current_sum)
        
        prev_deletions = current_deletions
        prev_prefix_sum = current_prefix_sum
    
    return prev_prefix_sum[-1] % MOD


class E1twilightandancientscrolleasierversionRewardCalculator(BaseRewardCalculator):
    """E1twilightandancientscrolleasierversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_answer']
    
    # 其他额外方法

