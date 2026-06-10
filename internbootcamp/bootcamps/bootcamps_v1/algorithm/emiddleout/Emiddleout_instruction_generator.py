import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
from collections import Counter




class EmiddleoutInstructionGenerator(BaseInstructionGenerator):
    """Emiddleout Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, solvable_probability=0.5):
        """
        初始化Emiddleout指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            solvable_probability: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.min_n = min_n
        self.max_n = max_n
        self.solvable_probability = solvable_probability
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        if random.random() < self.solvable_probability:
            # Generate valid permutations with same character composition
            t = ''.join(random.choices(string.ascii_lowercase, k=n))
            s_list = list(t)
            random.shuffle(s_list)
            s = ''.join(s_list)
        else:
            # Generate guaranteed different composition
            t = ''.join(random.choices(string.ascii_lowercase, k=n))
            while True:
                s = ''.join(random.choices(string.ascii_lowercase, k=n))
                if Counter(s) != Counter(t):
                    break
        
        expected_answer = self.compute_min_moves(s, t) if Counter(s) == Counter(t) else -1
        return {
            'n': n,
            's': s,
            't': t,
            'expected_answer': expected_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""## Middle-out字符串转换问题
给定两个长度均为{question_case['n']}的字符串：
s = "{question_case['s']}"
t = "{question_case['t']}"

每次操作可以选择s中的一个字符移动到开头或末尾。请计算将s转换为t所需的最小操作次数（如果无法完成返回-1）。

答案格式要求：将最终数值答案放在[answer]标签内，例如：[answer]3[/answer]或[answer]-1[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_moves(s, t):
        n = len(s)
        min_moves = n  # Initialize with maximum possible moves

        for i in range(n):
            t_ptr = i  # Start matching from position i in target
            s_ptr = 0  # Pointer for source string

            while s_ptr < n and t_ptr < n:
                if s[s_ptr] == t[t_ptr]:
                    t_ptr += 1  # Match found, move to next target character
                s_ptr += 1  # Always move source pointer

            # Calculate required moves: i (prefix) + remaining characters (suffix)
            current_moves = i + (n - t_ptr)
            min_moves = min(min_moves, current_moves)

        return min_moves if min_moves < n else -1
