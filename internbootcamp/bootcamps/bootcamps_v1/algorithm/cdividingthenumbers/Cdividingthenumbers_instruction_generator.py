import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CdividingthenumbersInstructionGenerator(BaseInstructionGenerator):
    """Cdividingthenumbers Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=60000):
        """
        初始化Cdividingthenumbers指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = max(int(min_n), 2)
        self.max_n = min(int(max_n), 60000)
        if self.max_n < self.min_n:
            self.max_n = self.min_n
    
    def case_generator(self):
        # 强制生成覆盖不同余数情况的测试用例
        candidates = []
        for _ in range(3):  # 每种余数至少生成一个案例
            n = random.randint(self.min_n, self.max_n)
            candidates.append(n)
        # 确保至少包含每个余数类型中的一个案例
        for remainder in [0, 1, 2, 3]:
            base_n = random.randint(3, 15) * 4 + remainder
            if 2 <= base_n <= 60000:
                candidates.append(base_n)
        n = random.choice(candidates)
        
        total_sum = n * (n + 1) // 2
        remainder = n % 4
        correct_diff = 0 if (remainder == 0 or remainder ==3) else 1
        return {
            'n': n,
            'correct_diff': correct_diff,
            'total_sum': total_sum,
            'remainder_class': remainder  # 增加余数分类用于调试
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return f"""Petya has integers from 1 to {n}. Split them into two non-empty groups to minimize the absolute difference of their sums.

Output format:
[answer]
<min_difference>
<group_size> <element1> <element2> ... <elementK>
[/answer]

Examples:
For n=4:
[answer]
0
2 1 4
[/answer]

For n=2:
[answer]
1
1 1
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

