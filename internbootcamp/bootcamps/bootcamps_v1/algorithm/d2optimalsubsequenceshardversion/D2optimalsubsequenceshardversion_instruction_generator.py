import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class D2optimalsubsequenceshardversionInstructionGenerator(BaseInstructionGenerator):
    """D2optimalsubsequenceshardversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=5, a_min=1, a_max=100):
        """
        初始化D2optimalsubsequenceshardversion指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            a_min: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.a_min = a_min
        self.a_max = a_max
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        a = [random.randint(self.a_min, self.a_max) for _ in range(n)]
        m = random.randint(1, self.max_m)
        
        # 按照算法构造最优子序列
        sorted_with_index = sorted([(-val, idx) for idx, val in enumerate(a)])
        cache = {}
        
        for k in range(1, n+1):
            selected = sorted(sorted_with_index[:k], key=lambda x: x[1])
            cache[k] = [a[x[1]] for x in selected]
        
        queries = [(random.randint(1, n), random.randint(1, k)) for k in [random.randint(1, n) for _ in range(m)]]
        
        return {
            'n': n,
            'a': a,
            'm': m,
            'queries': queries,
            '_cache': cache
        }
    
    @staticmethod
    def prompt_func(question_case):
        a_str = ' '.join(map(str, question_case['a']))
        queries = '\n'.join(f"{k} {pos}" for k, pos in question_case['queries'])
        return f"""Given sequence: {a_str}
Answer {question_case['m']} queries about the optimal subsequence:
{queries}

Format answers in [answer] tags with one number per line:
[answer]
{{answers}}
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

