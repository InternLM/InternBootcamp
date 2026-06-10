import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import deque
from collections import defaultdict




class CkingspathRewardCalculator(BaseRewardCalculator):
    """Ckingspath奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 允许数字前后有空格
        pattern = r'\[answer\]\s*(-?\d+)\s*\[/answer\]'
        matches = re.findall(pattern, output, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 构建允许区域字典
        allowed = defaultdict(set)
        for r, a, b in identity['segments']:
            allowed[r].update(range(a, b+1))
        
        start = identity['start']
        end = identity['end']
        
        # 快速检查起点终点合法性
        if start[0] not in allowed or start[1] not in allowed[start[0]]:
            return solution == -1
        if end[0] not in allowed or end[1] not in allowed[end[0]]:
            return solution == -1
        
        # BFS优化实现
        visited = {}
        queue = deque()
        queue.append((start[0], start[1], 0))
        visited[(start[0], start[1])] = 0
        
        while queue:
            x, y, steps = queue.popleft()
            
            # 到达终点立即返回
            if (x, y) == end:
                return solution == steps
            
            # 生成8个方向
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x+dx, y+dy
                    # 快速有效性检查
                    if nx not in allowed or ny not in allowed[nx]:
                        continue
                    # 更新最短路径
                    if (nx, ny) not in visited or steps+1 < visited[(nx, ny)]:
                        visited[(nx, ny)] = steps + 1
                        queue.append((nx, ny, steps+1))
        
        # 未找到路径
        return solution == -1
    
    # 其他额外方法

