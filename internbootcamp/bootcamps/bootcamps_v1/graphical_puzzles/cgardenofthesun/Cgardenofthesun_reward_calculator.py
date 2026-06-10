import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque
import re




class CgardenofthesunRewardCalculator(BaseRewardCalculator):
    """Cgardenofthesun奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        return [line.strip() for line in last_match.split('\n') if line.strip()]
    
    @classmethod
    def _verify_correction(cls, solution, case):
        try:
            # 基础格式验证
            if not solution or len(solution) != case['n']:
                return False
            if any(len(line) != case['m'] for line in solution):
                return False
            if any(c not in ('X', '.') for line in solution for c in line):
                return False
            
            # 保留原始X验证
            initial_x = {(i,j) for i, line in enumerate(case['initial_grid']) 
                        for j, c in enumerate(line) if c == 'X'}
            for i, j in initial_x:
                if solution[i][j] != 'X':
                    return False
            
            # 收集所有X坐标
            x_cells = [(i,j) for i, line in enumerate(solution)
                      for j, c in enumerate(line) if c == 'X']
            
            # 空验证
            if not x_cells:
                return False
            
            # 连通性验证
            visited = set()
            queue = deque([x_cells[0]])
            visited.add(x_cells[0])
            directions = [(-1,0), (0,1), (1,0), (0,-1)]
            
            while queue:
                x, y = queue.popleft()
                for dx, dy in directions:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < case['n'] and 0 <= ny < case['m']:
                        if solution[nx][ny] == 'X' and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
            
            if len(visited) != len(x_cells):
                return False
            
            # 树结构验证（边数 = 节点数 - 1）
            edge_count = 0
            for x, y in x_cells:
                for dx, dy in directions:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < case['n'] and 0 <= ny < case['m']:
                        if solution[nx][ny] == 'X':
                            edge_count += 1
            return (edge_count // 2) == (len(x_cells) - 1)
        
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    # 其他额外方法

