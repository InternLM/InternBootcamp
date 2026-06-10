import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
import re

# === 源文件中的全局函数 ===

def solve(n, m, k, c_list, p_matrix):
    INF = 10**18
    c = c_list
    p = p_matrix

    # DP优化算法实现
    dp = [[INF]*(m+1) for _ in range(k+1)]
    dp[0][0] = 0  # 初始状态
    
    for tree_idx in range(n):
        current_color = c[tree_idx]
        new_dp = [[INF]*(m+1) for _ in range(k+1)]
        
        for groups in range(k+1):
            for prev_color in range(m+1):
                if dp[groups][prev_color] == INF:
                    continue
                
                for new_color in range(1, m+1):
                    if current_color != 0 and current_color != new_color:
                        continue  # 已染色树不能改变颜色
                    
                    # 计算新分组数
                    new_groups = groups + (1 if new_color != prev_color else 0)
                    if new_groups > k:
                        continue
                    
                    # 计算成本
                    cost = p[tree_idx][new_color-1] if current_color == 0 else 0
                    
                    new_dp[new_groups][new_color] = min(
                        new_dp[new_groups][new_color],
                        dp[groups][prev_color] + cost
                    )
        
        dp = new_dp

    min_cost = min(dp[k][color] for color in range(1, m+1))
    return min_cost if min_cost < INF else -1


class CcoloringtreesRewardCalculator(BaseRewardCalculator):
    """Ccoloringtrees奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强的正则匹配模式
        pattern = r'\[answer\][\s\n]*(-?\d+)[\s\n]*\[/answer\]'
        matches = re.findall(pattern, output, re.IGNORECASE|re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1])
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 严格验证答案
        return solution == identity['ans']
    
    # 其他额外方法

