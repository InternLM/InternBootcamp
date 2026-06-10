import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DtimetorunInstructionGenerator(BaseInstructionGenerator):
    """Dtimetorun Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=50, min_m=1, max_m=50, possible_prob=0.5, max_k=10**4):
        """
        初始化Dtimetorun指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
            possible_prob: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
        self.possible_prob = possible_prob
        self.max_k = max_k  # 控制可验证的k上限
    
    def case_generator(self):
        """生成有效的谜题实例，确保k在可验证范围内"""
        while True:
            n = random.randint(self.min_n, self.max_n)
            m = random.randint(self.min_m, self.max_m)
            max_roads = 4 * n * m - 2 * n - 2 * m
            max_roads = max(max_roads, 0)  # 确保非负
            
            if max_roads == 0:
                # 无法生成可行案例
                k = random.randint(1, 10**9)
            else:
                if random.random() < self.possible_prob:
                    # 生成可行案例
                    k = random.randint(1, min(max_roads, self.max_k))
                else:
                    # 生成不可行案例
                    k = random.randint(max_roads + 1, 10**9)
            return {'n': n, 'm': m, 'k': k}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        k = question_case['k']
        return f"""Dtimetorun needs to run exactly {k} km in a {n}x{m} grid. Roads are one-way between adjacent cells. Rules:
- Start at top-left (1,1)
- Each move is U/D/L/R
- No road reuse
- Exactly {k} moves

Format answer as:
[answer]
YES/NO
[if YES]
a
f₁ s₁
...
fₐ sₐ
[/answer]

Example (n=3, m=3, k=4):
[answer]
YES
2
2 R
2 L
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

