import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict
from collections import deque

# === 源文件中的全局函数 ===

def simulate_knights_placement(initial_knights):
    current_knights = set()
    coords = [tuple(knight) for knight in initial_knights]
    if len(coords) != len(set(coords)):
        return 0
    for x, y in coords:
        if not (-1e9 <= x <= 1e9 and -1e9 <= y <= 1e9):
            return 0
    current_knights = set(coords)
    knight_moves = [(1,2), (1,-2), (-1,2), (-1,-2), (2,1), (2,-1), (-2,1), (-2,-1)]
    attack_counts = defaultdict(int)
    for x, y in current_knights:
        for dx, dy in knight_moves:
            neighbor = (x + dx, y + dy)
            attack_counts[neighbor] += 1
    queue = deque()
    in_queue = set()
    for cell in attack_counts:
        if attack_counts[cell] >=4 and cell not in current_knights:
            queue.append(cell)
            in_queue.add(cell)
    while queue:
        cell = queue.popleft()
        in_queue.discard(cell)
        if cell in current_knights:
            continue
        if attack_counts[cell] <4:
            continue
        current_knights.add(cell)
        for dx, dy in knight_moves:
            neighbor = (cell[0] + dx, cell[1] + dy)
            attack_counts[neighbor] += 1
            if attack_counts[neighbor] >=4 and neighbor not in current_knights and neighbor not in in_queue:
                queue.append(neighbor)
                in_queue.add(neighbor)
    return len(current_knights)


class CknightsRewardCalculator(BaseRewardCalculator):
    """Cknights奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        coords = []
        for line in last_match.split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            try:
                x = int(parts[0])
                y = int(parts[1])
                coords.append((x, y))
            except ValueError:
                continue
        return coords if coords else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or not isinstance(solution, list):
            return False
        n = identity['n']
        if len(solution) != n:
            return False
        if len(set(solution)) != n:
            return False
        for x, y in solution:
            if not (-1e9 <= x <= 1e9 and -1e9 <= y <= 1e9):
                return False
        required = (n ** 2) // 10
        final_count = simulate_knights_placement(solution)
        return final_count >= required
    
    # 其他额外方法

