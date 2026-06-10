import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CmaximumsplittingInstructionGenerator(BaseInstructionGenerator):
    """Cmaximumsplitting Bootcamp指令生成器"""
    
    def __init__(self, max_n=10**9, **params):
        """
        初始化Cmaximumsplitting指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_n = max_n  # 修正：遵守题目1e9的上限要求
    
    def case_generator(self):
        # 生成策略优化：按余数分布生成代表性案例
        case_type = random.choice(['edge', 'normal'] * 3 + ['remainder_case'])
        
        if case_type == 'edge':
            n = random.choice([
                1, 2, 3, 4, 5, 6, 7, 8, 9,
                12, 15, 16, 20, 21, 10**9
            ])
        elif case_type == 'remainder_case':
            rem = random.choice([0, 1, 2, 3])
            min_val = {0:4, 1:9, 2:6, 3:15}[rem]
            n = random.randint(min_val, min(self.max_n, min_val + 100))
            n = (n - rem) // 4 * 4 + rem  # 强制对齐余数
        else:
            n = random.randint(4, self.max_n)

        # 确保n不超过限制
        n = min(n, self.max_n)
        expected = self.calculate_answer(n)
        return {'n': n, 'expected': expected}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return f"""You are given a positive integer n. Your task is to represent n as a sum of the maximum possible number of composite numbers. If impossible, return -1.

Input:
n = {n}

Rules:
1. Composite number: integer >1 that is not prime
2. Summands must be composite numbers
3. Maximize the number of summands
4. Return -1 if impossible

Examples:
n=12 → 3 (4+4+4)
n=6 → 1 (6)
n=8 → 2 (4+4)
n=9 → -1 (9=9但必须拆分成多个数)

Answer format: 
[answer]<integer>[/answer]

Your answer must be within [answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def calculate_answer(self, n):
        """严格遵循参考代码逻辑的实现"""
        if n <= 3:
            return -1
        rem = n % 4
        correction_map = {
            0: (0, 0),
            1: (9, -1),  # 保证n >= 9
            2: (6, 0),   # 保证n >= 6
            3: (15, -1)  # 保证n >= 15
        }
        base, offset = correction_map.get(rem, (0, 0))

        if n < base:
            return -1

        count = (n - base) // 4 + offset
        return count if count > 0 else -1
