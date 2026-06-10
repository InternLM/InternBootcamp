import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class BdistinctpathsRewardCalculator(BaseRewardCalculator):
    """Bdistinctpaths奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        start = output.rfind('[answer]')
        if start == -1:
            return None
        end = output.find('[/answer]', start)
        if end == -1:
            return None
        answer_str = output[start + 8:end].strip()
        if not answer_str:
            return None
        if not answer_str.isdigit():
            return None
        return int(answer_str)
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        m = identity['m']
        k = identity['k']
        board = identity['board']
        
        # 检查初始棋盘是否有冲突
        for i in range(n):
            for j in range(m):
                current = board[i][j]
                if current == 0:
                    continue
                if (i > 0 and board[i-1][j] == current) or (j > 0 and board[i][j-1] == current):
                    return solution == 0
        
        memo = {}
        def dfs(x, y, mask):
            if (x, y, mask) in memo:
                return memo[(x, y, mask)]
            if x == n and y == m:
                return 1
            res = 0
            for color in range(1, k+1):
                if not (mask & (1 << (color - 1))):
                    if board[x-1][y-1] == 0 or board[x-1][y-1] == color:
                        new_mask = mask | (1 << (color - 1))
                        if y < m:
                            res += dfs(x, y+1, new_mask)
                        else:
                            res += dfs(x+1, 1, new_mask)
            memo[(x, y, mask)] = res % MOD
            return memo[(x, y, mask)]
        
        total = dfs(1, 1, 0) % MOD
        return solution == total
    
    # 其他额外方法

