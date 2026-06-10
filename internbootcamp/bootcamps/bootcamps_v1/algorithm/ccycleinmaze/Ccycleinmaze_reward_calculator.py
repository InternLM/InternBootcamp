import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import deque
import random
import re




class CcycleinmazeRewardCalculator(BaseRewardCalculator):
    """Ccycleinmaze奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 提取最后一个答案并标准化格式
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL|re.IGNORECASE)
        if not matches:
            return None
        raw = matches[-1].strip().upper().replace(' ', '')
        # 过滤无效字符
        cleaned = ''.join([c for c in raw if c in {'D','L','R','U'}])
        return cleaned if (cleaned and len(cleaned) == len(raw)) else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 处理特殊case
        if solution == "IMPOSSIBLE":
            return identity['correct_answer'] == "IMPOSSIBLE"
        
        # 验证路径合法性
        k = identity['k']
        if len(solution) != k or k % 2 != 0:
            return False
        
        n, m = identity['n'], identity['m']
        grid = identity['grid']
        dir_map = {'D': (1,0), 'L': (0,-1), 'R': (0,1), 'U': (-1,0)}
        
        # 定位起点
        start_x, start_y = -1, -1
        for i in range(n):
            for j in range(m):
                if grid[i][j] == 'X':
                    start_x, start_y = i, j
                    break
        
        x, y = start_x, start_y
        for move in solution:
            dx, dy = dir_map.get(move, (0,0))
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= n or ny < 0 or ny >= m or grid[nx][ny] == '*':
                return False
            x, y = nx, ny
        
        # 必须回到起点
        return (x, y) == (start_x, start_y)
    
    # 其他额外方法

