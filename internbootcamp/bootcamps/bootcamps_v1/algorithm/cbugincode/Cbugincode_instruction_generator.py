import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from itertools import combinations




class CbugincodeInstructionGenerator(BaseInstructionGenerator):
    """Cbugincode Bootcamp指令生成器"""
    
    def __init__(self, n_min=3, n_max=10, p_min=0, p_max=None):
        """
        初始化Cbugincode指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            p_min: 参数描述
            p_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n_min = max(3, n_min)  # 确保最小值为3
        self.n_max = min(300000, n_max)  # 设置题目上限
        self.p_min = max(0, p_min)
        self.p_max = p_max if p_max is not None else self.n_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        p = random.randint(max(self.p_min, 0), min(n, self.p_max))
        
        pairs = []
        for i in range(1, n+1):
            available = list(set(range(1, n+1)) - {i})
            while True:
                x, y = random.sample(available, 2)
                # 确保生成的pair保持原始顺序
                if x < y:  
                    pairs.append([x, y])
                    break
                elif y < x:
                    pairs.append([y, x])
                    break
        return {
            'n': n,
            'p': p,
            'pairs': pairs
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        p = question_case['p']
        pairs = question_case['pairs']
        problem = f"""## Programming Problem

**Background**:
A software bug occurred in a company with {n} coders. Each coder claimed two suspects. The CEO needs to select two suspects such that at least {p} coders approve the choice. A coder approves if at least one of their named suspects is selected.

**Input Format**:
- First line: n p
- Next {n} lines: x y (each coder's claim)

**Current Case**:
{n} {p}
"""
        problem += '\n'.join(f"{x} {y}" for x, y in pairs)
        problem += "\n\n**Output**: The number of valid pairs. Place your final answer within [answer][/answer] tags."
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

