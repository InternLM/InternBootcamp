import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class DgeneratingsetsInstructionGenerator(BaseInstructionGenerator):
    """Dgeneratingsets Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dgeneratingsets指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n = params.get('n', 5)
        self.max_number = params.get('max_number', 100)
    
    def case_generator(self):
        n = self.n
        max_num = self.max_number
        while True:
            X = random.sample(range(1, max_num + 1), n)
            Y = []
            for x in X:
                current = x
                k = random.randint(0, 10)
                for _ in range(k):
                    op = random.choice([0, 1])
                    if op == 0:
                        current = current * 2
                    else:
                        current = current * 2 + 1
                Y.append(current)
            Y = list(set(Y))
            if len(Y) >= n:
                Y = Y[:n]
                break
        Y.sort()
        return {'y': Y}
    
    @staticmethod
    def prompt_func(question_case):
        Y = question_case['y']
        y_str = ' '.join(map(str, Y))
        prompt = f"你是一个数学专家，现在需要解决一个数学谜题。给定一个集合Y={{ {y_str} }}，请找出一个集合X，使得X可以通过一系列操作生成Y。操作包括：将X中的元素乘以2，或者乘以2加1。X中的元素必须互不相同，并且X的最大元素尽可能小。请将X的元素以空格分隔的形式放在[answer]标签中，例如：[answer]4 5 2 3 1[/answer]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

