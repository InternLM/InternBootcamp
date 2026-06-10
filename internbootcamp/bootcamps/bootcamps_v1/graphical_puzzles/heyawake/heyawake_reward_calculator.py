import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
from collections import deque




class HeyawakeRewardCalculator(BaseRewardCalculator):
    """Heyawake奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = eval(last_match)
            if isinstance(solution, list) and all(isinstance(row, list) for row in solution):
                return solution
            return None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 验证solution结构合法性
        rows = identity['rows']
        cols = identity['cols']
        rooms = identity['rooms']
        if (not isinstance(solution, list) or len(solution) != rows or
            any(not isinstance(row, list) or len(row) != cols for row in solution)):
            return False
        for row in solution:
            for cell in row:
                if cell not in (0, 1):
                    return False
        
        # 规则1：黑格不能相邻
        for i in range(rows):
            for j in range(cols):
                if solution[i][j] == 1:
                    if j+1 < cols and solution[i][j+1] == 1:
                        return False
                    if i+1 < rows and solution[i+1][j] == 1:
                        return False
        
        # 规则2：房间约束
        for room in rooms:
            cells = room['cells']
            if 'number' in room:
                required = room['number']
                actual = sum(solution[i][j] for (i, j) in cells)
                if actual != required:
                    return False
        
        # 规则3：白格连通性
        white = [(i, j) for i in range(rows) for j in range(cols) if solution[i][j] == 0]
        if not white:
            return False
        visited = set()
        queue = deque([white[0]])
        visited.add(white[0])
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        while queue:
            i, j = queue.popleft()
            for dx, dy in directions:
                ni, nj = i+dx, j+dy
                if 0 <= ni < rows and 0 <= nj < cols and solution[ni][nj] == 0:
                    if (ni, nj) not in visited:
                        visited.add((ni, nj))
                        queue.append((ni, nj))
        if len(visited) != len(white):
            return False
        
        # 规则4：条纹防止规则
        # 构建房间映射
        room_id = [[-1 for _ in range(cols)] for _ in range(rows)]
        for idx, room in enumerate(rooms):
            for i, j in room['cells']:
                room_id[i][j] = idx
        
        # 检查行
        for i in range(rows):
            current_rooms = []
            for j in range(cols):
                if solution[i][j] == 1:
                    if len(current_rooms) >= 3:
                        return False
                    current_rooms = []
                else:
                    rid = room_id[i][j]
                    if not current_rooms or rid != current_rooms[-1]:
                        current_rooms.append(rid)
                    if len(current_rooms) >= 3:
                        return False
            if len(current_rooms) >= 3:
                return False
        
        # 检查列
        for j in range(cols):
            current_rooms = []
            for i in range(rows):
                if solution[i][j] == 1:
                    if len(current_rooms) >= 3:
                        return False
                    current_rooms = []
                else:
                    rid = room_id[i][j]
                    if not current_rooms or rid != current_rooms[-1]:
                        current_rooms.append(rid)
                    if len(current_rooms) >= 3:
                        return False
            if len(current_rooms) >= 3:
                return False
        
        return True
    
    # 其他额外方法

