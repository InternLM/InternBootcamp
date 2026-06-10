import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CgamblingInstructionGenerator(BaseInstructionGenerator):
    """Cgambling Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=5, max_value=10**6):
        """
        初始化Cgambling指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            max_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.max_value = max_value
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        a = [random.randint(1, self.max_value) for _ in range(n)]
        b = [random.randint(1, self.max_value) for _ in range(n)]
        return {'n': n, 'a': a, 'b': b}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a = question_case['a']
        b = question_case['b']
        problem = (
            "Two players A and B have lists of integers and take turns making optimal moves to maximize their score difference (A's score minus B's).\n\n"
            "Game Rules:\n"
            "1. Player A starts first. The game ends when both lists are empty.\n"
            "2. On a turn, a player can either:\n"
            "   - Take an element from their own list (adds to their score, element is removed)\n"
            "   - Remove an element from the opponent's list\n"
            "3. Both players play optimally to maximize their own advantage.\n\n"
            "Input Details:\n"
            f"- First line: n = {n} (size of each list)\n"
            f"- Second line (A's list): {', '.join(map(str, a))}\n"
            f"- Third line (B's list): {', '.join(map(str, b))}\n\n"
            "Compute the final score difference (A - B). Put your answer within [answer] and [/answer], e.g., [answer]0[/answer]."
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def calculate_correct_answer(cls, identity):
        n = identity['n']
        a = identity['a']
        b = identity['b']
        merged = []
        for x in a:
            merged.append((x, 1))
        for x in b:
            merged.append((x, 2))
        merged.sort()
        s1, s2 = 0, 0
        for i in range(1, 2 * n + 1):
            val, player = merged[2 * n - i]
            if i % 2 == 1:  # A's turn
                if player == 1:
                    s1 += val
            else:  # B's turn
                if player == 2:
                    s2 += val
        return s1 - s2
