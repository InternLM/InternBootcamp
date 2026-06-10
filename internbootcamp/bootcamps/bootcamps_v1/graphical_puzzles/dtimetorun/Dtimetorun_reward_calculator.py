import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class DtimetorunRewardCalculator(BaseRewardCalculator):
    """Dtimetorun奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_block = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_block:
            return None
        lines = [l.strip() for l in answer_block[-1].strip().split('\n')]
        
        if not lines:
            return None
        
        if lines[0].upper() == 'NO':
            return {'answer': 'NO'} if len(lines) == 1 else None
        
        if lines[0].upper() != 'YES' or len(lines) < 2:
            return None
        
        try:
            a = int(lines[1])
            if not (1 <= a <= 3000) or len(lines) < 2 + a:
                return None
        except:
            return None
        
        steps = []
        for line in lines[2:2+a]:
            parts = line.split()
            if len(parts) < 2:
                return None
            try:
                f = int(parts[0])
                s = ''.join(parts[1:]).upper()
                if not (1 <= f <= 1e9) or not (1 <= len(s) <=4) or any(c not in 'UDLR' for c in s):
                    return None
                steps.append((f, s))
            except:
                return None
        
        return {'answer': 'YES', 'steps': steps}
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n, m, k = identity['n'], identity['m'], identity['k']
        max_roads = 4 * n * m - 2 * n - 2 * m
        
        # 快速判断不可能情形
        if k > max_roads:
            return solution.get('answer') == 'NO'
        if solution.get('answer') != 'YES':
            return False
        
        steps = solution.get('steps', [])
        if len(steps) == 0 or len(steps) > 3000:
            return False
        
        total_moves = sum(f * len(s) for f, s in steps)
        if total_moves != k:
            return False
        
        # 路径模拟优化
        current = (1, 1)
        used = set()
        
        for f, s in steps:
            s = s.upper()
            # 处理单方向连续移动
            if len(set(s)) == 1:
                dir = s[0]
                dx, dy = {'U': (-1,0), 'D':(1,0), 'L':(0,-1), 'R':(0,1)}[dir]
                steps_needed = f * len(s)
                
                # 批量检查越界和道路重复
                x, y = current
                road_chain = []
                for _ in range(steps_needed):
                    nx, ny = x + dx, y + dy
                    if not (1 <= nx <= n and 1 <= ny <= m):
                        return False
                    road = ((x, y), (nx, ny))
                    if road in used or road in road_chain:
                        return False
                    road_chain.append(road)
                    x, y = nx, ny
                used.update(road_chain)
                current = (x, y)
            else:
                # 处理复杂路径
                for _ in range(f):
                    pos = current
                    step_roads = []
                    for move in s:
                        x, y = pos
                        dx, dy = {'U': (-1,0), 'D':(1,0), 'L':(0,-1), 'R':(0,1)}[move]
                        nx, ny = x + dx, y + dy
                        if not (1 <= nx <= n and 1 <= ny <= m):
                            return False
                        road = ((x, y), (nx, ny))
                        if road in used or road in step_roads:
                            return False
                        step_roads.append(road)
                        pos = (nx, ny)
                    used.update(step_roads)
                    current = pos
        return True
    
    # 其他额外方法

