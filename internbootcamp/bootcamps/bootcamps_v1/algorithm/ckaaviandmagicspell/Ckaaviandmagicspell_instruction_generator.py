import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CkaaviandmagicspellInstructionGenerator(BaseInstructionGenerator):
    """Ckaaviandmagicspell Bootcamp指令生成器"""
    
    def __init__(self, max_n=3000, min_m=1, default_m=2, default_n=4):
        """
        初始化Ckaaviandmagicspell指令生成器
        
        Args:
            max_n: 参数描述
            min_m: 参数描述
            default_m: 参数描述
            default_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'max_n': max_n,
            'min_m': min_m,
            'default_m': default_m,
            'default_n': default_n
        }
    
    def case_generator(self):
        m = random.randint(self.params['min_m'], self.params['default_m'])
        n = random.randint(m, self.params['default_n'])
        
        # 生成保证至少存在一个解的测试用例
        T = ''.join(random.choices('abc', k=m))
        
        # 构造合法S的核心部分（必须与T前缀匹配）
        op_sequence = []
        constructed = list(T)
        for _ in range(m):
            op = random.choice(['front', 'back'])
            op_sequence.append(op)
            if op == 'front':
                constructed.pop(0)  # 逆向构造
            else:
                constructed.pop()
        
        S_core = ''.join(constructed)
        
        # 补充随机字符
        if n > m:
            S_core += ''.join(random.choices('abc', k=n - m))
        
        return {"S": S_core, "T": T}
    
    @staticmethod
    def prompt_func(question_case):  # 原第44行
        S = question_case['S']
        T = question_case['T']
        prompt = f"""Ckaaviandmagicspell needs to determine the number of valid operation sequences when building string A from "{S}" that results in the prefix "{T}". 
Each operation chooses to prepend/append the next character from S. 
The answer must be a single integer within [answer][/answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

