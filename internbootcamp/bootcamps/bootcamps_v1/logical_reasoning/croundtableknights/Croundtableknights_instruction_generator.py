import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CroundtableknightsInstructionGenerator(BaseInstructionGenerator):
    """Croundtableknights Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=100, has_solution=None):
        """
        初始化Croundtableknights指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            has_solution: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.has_solution = has_solution  # None: random, True: yes, False: no
    
    def case_generator(self):
        generate_solution = self.has_solution if self.has_solution is not None else random.choice([True, False])
        n = random.randint(self.min_n, self.max_n)
        
        if generate_solution:
            possible_ls = [l for l in range(1, n//3 +1) if n % l == 0 and (n//l) >=3]
            if not possible_ls:
                l = 1  # 当n本身是素数时确保至少有一个有效分割
            else:
                l = random.choice(possible_ls)
            i = random.randint(0, l-1)
            status = [0] * n
            for j in range(i, n, l):
                status[j] = 1
            # 其他位置随机设置，但不影响存在解
            for j in range(n):
                if j % l != i % l:
                    status[j] = random.randint(0, 1)
        else:
            while True:
                status = [random.choice([0, 1]) for _ in range(n)]
                # 允许全0情况，因为全0必然无解
                if not self.__class__._is_lucky(n, status):
                    break
        
        return {'n': n, 'status': status}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        status = ' '.join(map(str, question_case['status']))
        return f"""Determine if the knights' moods allow forming a regular polygon. Knights are arranged around a round table. 
A regular polygon requires at least 3 vertices (knights in good mood). 

Input:
{n}
{status}

Output your answer (YES/NO) within [answer]...[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _is_lucky(n, status):
        for l in range(1, n//3 +1):
            if n % l != 0:
                continue
            k = n // l
            if k < 3:
                continue
            for i in range(l):
                if all(status[j] == 1 for j in range(i, n, l)):
                    return True
        return False
