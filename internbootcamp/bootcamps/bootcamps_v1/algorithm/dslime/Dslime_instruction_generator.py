import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DslimeInstructionGenerator(BaseInstructionGenerator):
    """Dslime Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, allow_positive=True, allow_negative=True, min_val=-100, max_val=100):
        """
        初始化Dslime指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            allow_positive: 参数描述
            allow_negative: 参数描述
            min_val: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 参数有效性验证
        if min_n < 1:
            raise ValueError("min_n must be at least 1")
        if max_n < min_n:
            raise ValueError("max_n must be >= min_n")
        if min_val > max_val:
            raise ValueError("Invalid value range: min_val > max_val")
        if not allow_positive and not allow_negative:
            if not (min_val <= 0 and max_val >= 0):
                raise ValueError("When both signs disabled, value range must include 0")

        self.min_n = min_n
        self.max_n = max_n
        self.allow_positive = allow_positive
        self.allow_negative = allow_negative
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        # 调整有效取值范围
        effective_min = max(0, self.min_val) if not self.allow_negative else self.min_val
        effective_max = min(0, self.max_val) if not self.allow_positive else self.max_val

        n = random.randint(self.min_n, self.max_n)
        if n == 1:
            return {'n': 1, 'a': [random.randint(effective_min, effective_max)]}

        # 确定可能生成的案例类型
        case_types = []
        
        # 混合类型需要同时支持正负数
        if self.allow_positive and self.allow_negative:
            if effective_min <= -1 and effective_max >= 1:
                case_types.append('mixed')
        
        # 全正数类型要求至少能生成正数
        if self.allow_positive and effective_max >= 1:
            case_types.append('positive')
        
        # 全负数类型要求至少能生成负数
        if self.allow_negative and effective_min <= -1:
            case_types.append('negative')

        # 处理无法生成有效类型的情况
        if not case_types:
            return {'n': n, 'a': [0]*n}

        case_type = random.choice(case_types)
        a = []

        if case_type == 'mixed':
            # 强制生成至少一个正数和负数
            positive_pos = random.randint(0, n-1)
            negative_pos = random.choice([i for i in range(n) if i != positive_pos])
            
            a = [random.randint(effective_min, effective_max) for _ in range(n)]
            a[positive_pos] = abs(a[positive_pos]) + 1  # 确保正数
            a[negative_pos] = -abs(a[negative_pos]) - 1  # 确保负数

        elif case_type == 'positive':
            # 保证至少一个正数
            a = [random.randint(0, effective_max) for _ in range(n)]
            a[random.randint(0, n-1)] = random.randint(1, effective_max)

        elif case_type == 'negative':
            # 全负数
            a = [random.randint(effective_min, -1) for _ in range(n)]

        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n, a = question_case['n'], question_case['a']
        return f"""Solve this slime puzzle where {n} slimes with values {a} merge until one remains. 
The rules are: Each slime can eat adjacent neighbors, merging x and y becomes x-y. 
Find the maximum possible final value. Put your answer in [answer]...[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

