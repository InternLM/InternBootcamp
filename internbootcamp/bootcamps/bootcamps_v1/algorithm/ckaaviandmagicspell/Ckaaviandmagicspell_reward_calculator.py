import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CkaaviandmagicspellRewardCalculator(BaseRewardCalculator):
    """Ckaaviandmagicspell奖励计算器"""
    
    @staticmethod
    def extract_output(output):  # 此处修复缩进问题
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        MOD = 998244353
        S = identity['S']
        T = identity['T']
        n, m = len(S), len(T)
        
        # 边界条件处理
        if m == 0 or n < m:
            return solution == 0
        
        # 动态规划验证核心逻辑
        dp = [[0]*(n+1) for _ in range(n+1)]
        dp[0][0] = 1
        
        for step in range(n):
            for pos in range(n+1):
                if dp[step][pos] == 0:
                    continue
                
                c = S[step]
                # 前置分支
                if pos > 0 and (pos-1 >= m or T[pos-1] == c):
                    dp[step+1][pos-1] = (dp[step+1][pos-1] + dp[step][pos]) % MOD
                # 后置分支
                end_pos = pos + step
                if end_pos >= m or (end_pos < m and T[end_pos] == c):
                    dp[step+1][pos] = (dp[step+1][pos] + dp[step][pos]) % MOD
        
        total = sum(dp[j][0] for j in range(m, n+1)) % MOD
        return solution == total
    
    # 其他额外方法

