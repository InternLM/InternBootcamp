import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import re
import random




class CfirstdigitlawRewardCalculator(BaseRewardCalculator):
    """Cfirstdigitlaw奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]([\d.eE+-]+)\s*\[/answer\]', output)
        if not matches:
            return None
        try:
            return float(matches[-1].strip().replace(',', ''))
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            N = identity['N']
            variables = identity['variables']
            K = identity['K']
            
            # 动态规划数组初始化
            dp = [1.0] + [0.0] * N
            
            for var in variables:
                L, R = var['L'], var['R']
                total = R - L + 1
                
                # 计算有效数目
                valid_count = 0
                c = 1
                while c <= 1e18:
                    lower_bound = max(L, c)
                    upper_bound = min(R, 2 * c - 1)
                    valid_count += max(0, upper_bound - lower_bound + 1)
                    c *= 10
                
                # 更新概率分布
                p = valid_count / total
                new_dp = [0.0] * (N + 1)
                new_dp[0] = dp[0] * (1 - p)
                for j in range(1, N + 1):
                    new_dp[j] = dp[j] * (1 - p) + dp[j-1] * p
                dp = new_dp
            
            # 计算阈值
            required = (N * K + 99) // 100
            threshold = max(0, min(required, N))
            correct_prob = sum(dp[threshold:]) if threshold <= N else 0.0
            
            # 浮点数精确校验
            return math.isclose(solution, correct_prob, rel_tol=1e-9, abs_tol=1e-12)
        except:
            return False
    
    # 其他额外方法

