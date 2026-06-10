import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CserejaandtwosequencesInstructionGenerator(BaseInstructionGenerator):
    """Cserejaandtwosequences Bootcamp指令生成器"""
    
    def __init__(self, k=3, n=5, m=5, e=1000):
        """
        初始化Cserejaandtwosequences指令生成器
        
        Args:
            k: 参数描述
            n: 参数描述
            m: 参数描述
            e: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.k = k  # Expected correct answer (maximum number of moves)
        self.n = n  # Length of sequence a
        self.m = m  # Length of sequence b
        self.e = e  # Energy cost per move of type 1
    
    def case_generator(self):
        # Generate k unique common elements
        common = list(range(1, self.k + 1))
        
        # Build sequence a with the common elements followed by unique elements
        a = common.copy()
        used_a = set(common)
        remaining_a = []
        while len(remaining_a) < self.n - self.k:
            num = random.randint(self.k + 1, 100000)
            if num not in used_a:
                remaining_a.append(num)
                used_a.add(num)
        a += remaining_a[:self.n - self.k]
        
        # Build sequence b with the same common elements followed by unique elements not overlapping with a's remaining
        b = common.copy()
        used_b = set(common)
        remaining_b = []
        while len(remaining_b) < self.m - self.k:
            num = random.randint(self.k + 10001, 200000)  # Ensure no overlap with a's remaining
            if num not in used_b:
                remaining_b.append(num)
                used_b.add(num)
        b += remaining_b[:self.m - self.k]
        
        # Calculate s to ensure it's exactly enough for k moves plus the remaining elements cost
        s = self.k * self.e + (self.n + self.m - 2 * self.k)
        
        return {
            'n': self.n,
            'm': self.m,
            's': s,
            'e': self.e,
            'a': a,
            'b': b,
            'correct_k': self.k
        }
    
    @staticmethod
    def prompt_func(question_case):
        a_str = ' '.join(map(str, question_case['a']))
        b_str = ' '.join(map(str, question_case['b']))
        prompt = (
            "Sereja has two sequences of integers and can perform two types of operations to earn dollars. Each move of type 1 costs a fixed energy (e) and earns $1. Move type 2 removes all remaining elements, costing energy equal to the number of elements left. Determine the maximum dollars Sereja can earn without his energy dropping below zero.\n\n"
            "Input format:\n"
            "- First line: n m s e (sequence lengths, initial energy, energy cost per move type 1)\n"
            "- Second line: a_1 a_2 ... a_n\n"
            "- Third line: b_1 b_2 ... b_m\n\n"
            f"Input:\n{question_case['n']} {question_case['m']} {question_case['s']} {question_case['e']}\n"
            f"{a_str}\n"
            f"{b_str}\n\n"
            "Output the maximum dollars as an integer enclosed within [answer] and [/answer], e.g., [answer]3[/answer].\n"
            "Output:\n"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

