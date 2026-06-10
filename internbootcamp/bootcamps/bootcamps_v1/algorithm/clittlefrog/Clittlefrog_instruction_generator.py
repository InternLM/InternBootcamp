import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class ClittlefrogInstructionGenerator(BaseInstructionGenerator):
    """Clittlefrog Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Clittlefrog指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)  # 默认n为5
    
    def case_generator(self):
        # 生成随机n在1到100之间
        n = random.randint(1, 100)
        solution = self._generate_solution(n)
        return {'n': n, 'solution': solution}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        prompt = f"Vasya the frog needs to visit {n} mounds in a line, each exactly once. Each jump between consecutive mounds must be a unique distance. Generate a permutation of 1 to {n} such that the absolute differences between consecutive elements are all unique. Output your answer as space-separated integers within [answer] tags. For example, if n=3, a valid answer is [answer]1 3 2[/answer]."
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_solution(self, n):
        if n == 1:
            return [1]
        solution = []
        i = 1
        j = n
        while i <= j:
            solution.append(i)
            if i != j:
                solution.append(j)
            i += 1
            j -= 1
        # 确保长度正确，处理n为奇数的情况
        return solution[:n]
