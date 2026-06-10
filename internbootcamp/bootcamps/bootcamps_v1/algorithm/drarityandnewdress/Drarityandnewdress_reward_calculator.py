import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class DrarityandnewdressRewardCalculator(BaseRewardCalculator):
    """Drarityandnewdress奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.DOTALL)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            m = identity['m']
            grid = identity['grid']
            
            # 保证输入有效性
            if n <= 0 or m <= 0 or len(grid) != n or any(len(row)!=m for row in grid):
                return False
            if not all(c.islower() and c.isalpha() for row in grid for c in row):
                return False

            # 构造带保护圈的矩阵
            wall = 'W' * (m + 2)
            mat = [wall]  # 上保护墙
            mat.extend(f'W{row}W' for row in grid)
            mat.append(wall)  # 下保护墙

            # 初始化DP表
            dp = [[1]*(m+2) for _ in range(n+2)]
            
            # 设置边界条件
            for i in range(n+2):
                dp[i][0] = dp[i][m+1] = 0
            for j in range(m+2):
                dp[0][j] = dp[n+1][j] = 0

            # 动态规划计算
            for i in range(1, n+1):
                for j in range(1, m+1):
                    current_color = mat[i][j]
                    neighbors = [
                        mat[i-1][j-1],
                        mat[i-1][j],
                        mat[i-1][j+1]
                    ]
                    
                    if all(c == current_color for c in neighbors):
                        depth = min(dp[i-1][j-1], dp[i-1][j], dp[i-1][j+1])
                        height = 2 * depth
                        
                        if i > height and mat[i - height][j] == current_color:
                            dp[i][j] = depth + 1
                        else:
                            dp[i][j] = depth
                    else:
                        dp[i][j] = 1  # 重置为基本单元

            correct = sum(sum(row[1:-1]) for row in dp[1:-1])
            return solution == correct
            
        except Exception:
            return False
    
    # 其他额外方法

