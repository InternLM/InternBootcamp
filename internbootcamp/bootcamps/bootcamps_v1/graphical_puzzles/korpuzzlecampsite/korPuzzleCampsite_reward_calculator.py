import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from itertools import product




class KorpuzzlecampsiteRewardCalculator(BaseRewardCalculator):
    """Korpuzzlecampsite奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 匹配最后一个[[...]]结构
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        
        # 清理并分割行列
        rows = [row.strip() for row in last_match.split(',') if row.strip()]
        solution = []
        for row in rows:
            elements = re.split(r'\s+', row.strip())
            cleaned = [e.upper().replace('，', ',') for e in elements if e]
            solution.append(cleaned)
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            grid = identity['grid']
            row_clues = identity['row_clues']
            col_clues = identity['col_clues']
            n, m = len(grid), len(grid[0])
            
            # 1. 检查解的结构有效性
            if len(solution) != n:
                return False
            if any(len(row) != m for row in solution):
                return False
            
            # 2. 验证原树位置保留
            for i in range(n):
                for j in range(m):
                    if grid[i][j] == 'T' and solution[i][j] != 'T':
                        return False
            
            # 3. 验证行约束
            for i in range(n):
                if solution[i].count('C') != row_clues[i]:
                    return False
            
            # 4. 验证列约束
            for j in range(m):
                col_count = sum(solution[i][j] == 'C' for i in range(n))
                if col_count != col_clues[j]:
                    return False
            
            # 5. 验证帐篷放置规则
            for i in range(n):
                for j in range(m):
                    if solution[i][j] != 'C':
                        continue
                    
                    # 5.1 检查与树相邻
                    has_tree = False
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        x, y = i+dx, j+dy
                        if 0 <= x < n and 0 <= y < m:
                            if solution[x][y] == 'T':
                                has_tree = True
                                break
                    if not has_tree:
                        return False
                    
                    # 5.2 检查帐篷相邻
                    for dx in [-1,0,1]:
                        for dy in [-1,0,1]:
                            if dx == 0 and dy == 0:
                                continue
                            x, y = i+dx, j+dy
                            if 0 <= x < n and 0 <= y < m:
                                if solution[x][y] == 'C':
                                    return False
            return True
        except Exception as e:
            print(f"验证异常：{str(e)}")
            return False
    
    # 其他额外方法

