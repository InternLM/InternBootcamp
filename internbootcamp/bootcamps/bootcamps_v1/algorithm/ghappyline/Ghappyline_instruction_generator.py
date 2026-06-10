import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class GhappylineInstructionGenerator(BaseInstructionGenerator):
    """Ghappyline Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=1000, solvable_probability=0.5, value_range=(0, 10**9)):
        """
        初始化Ghappyline指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            solvable_probability: 参数描述
            value_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.min_n = min_n
        self.max_n = max_n
        self.solvable_probability = solvable_probability
        self.value_range = value_range
    
    def case_generator(self):
        if random.random() < self.solvable_probability:
            return self.generate_solvable_case()
        else:
            return self.generate_unsolvable_case()
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        return f"""As the ice cream stall manager in Berland, determine if residents can swap positions (costing $1 per swap) to create a non-decreasing money sequence from front to back.

Input:
{n}
{a}

Rules:
1. Swaps consume $1 from the forward-moving person
2. Positions are numbered from the queue end (position 0 = last)
3. Output the modified amounts or ":(" if impossible

Format your answer within [answer]...[/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_solvable_case(self):
        n = random.randint(self.min_n, self.max_n)
        current = random.randint(*self.value_range)
        sorted_values = [current]
        for _ in range(1, n):
            current += random.randint(1, 100)
            sorted_values.append(current)
        a = [sorted_values[i] - i for i in range(n)]
        random.shuffle(a)
        return {'n': n, 'a': a}

    def generate_unsolvable_case(self):
        n = random.randint(2, self.max_n)
        # 确保至少有一个重复对
        duplicate_value = random.randint(*self.value_range) + n//2  # 提升冲突概率
        processed_values = [duplicate_value - i for i in range(n)]
        # 随机插入一个重复值
        idx = random.randint(0, n-2)
        processed_values[idx] = processed_values[idx+1] = duplicate_value
        a = [x - i for i, x in enumerate(processed_values)]
        return {'n': n, 'a': a}
