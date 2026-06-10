import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CknightsInstructionGenerator(BaseInstructionGenerator):
    """Cknights Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=1000, **kwargs):
        """
        初始化Cknights指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        if not (1 <= min_n <= max_n <= 1000):
            raise ValueError("n must satisfy 1 ≤ min_n ≤ max_n ≤ 1000")
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        return {'n': n}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        required = (n ** 2) // 10
        prompt = f"""You are solving a knight placement puzzle. The task is to arrange {n} knights on an infinite chessboard such that after Ivan's process of adding new knights, the total number becomes at least {required}.

Rules:
1. Initially, place exactly {n} knights on distinct cells.
2. Ivan repeatedly adds a knight to any free cell attacked by at least 4 existing knights until no such cells exist.
3. The final number of knights must be ≥ {required}.

Output:
Provide {n} unique coordinate pairs (x_i, y_i), each between -1e9 and 1e9. Format your answer inside [answer] and [/answer] tags.

Example Format for n=4:
[answer]
1 1
3 1
1 5
4 4
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

