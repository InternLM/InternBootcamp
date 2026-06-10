import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class BandsequencesInstructionGenerator(BaseInstructionGenerator):
    """Bandsequences Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Bandsequences指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.n_min = params.get('n_min', 2)
        self.n_max = params.get('n_max', 10)
        self.x_min = params.get('x_min', 0)
        self.x_max = params.get('x_max', 100)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        x = random.randint(self.x_min, self.x_max)
        c = random.randint(2, n)
        a = [x] * c
        for _ in range(n - c):
            a.append(random.randint(self.x_min, self.x_max))
        random.shuffle(a)
        return {
            'n': n,
            'a': a
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        a_str = ', '.join(map(str, a))
        prompt = (
            f"给定一个数组a，其中n={n}，数组元素为：{a}。找出所有符合条件的排列数目。输出结果模{MOD}。\n"
            f"一个排列是好的，当且仅当对于所有i从1到n-1，前i项的按位与等于后n-i项的按位与。\n"
            f"请将答案放在[answer]标签内，例如：[answer]42[/answer]。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

