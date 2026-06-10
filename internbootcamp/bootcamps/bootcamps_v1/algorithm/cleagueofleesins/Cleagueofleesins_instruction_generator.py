import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
import re




class CleagueofleesinsInstructionGenerator(BaseInstructionGenerator):
    """Cleagueofleesins Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cleagueofleesins指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', random.randint(5, 10))
        self.min_n = params.get('min_n', 5)
        self.max_n = params.get('max_n', 10)
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        p = list(range(1, n+1))
        random.shuffle(p)
        
        triples = []
        for i in range(n-2):
            triplet = p[i:i+3]
            random.shuffle(triplet)
            triples.append(tuple(triplet))
        
        random.shuffle(triples)
        return {'n': n, 'triples': triples}
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [str(question_case['n'])] + \
            [' '.join(map(str, t)) for t in question_case['triples']]
        input_example = '\n'.join(input_lines)
        
        return f"""你正在解决排列重建问题。给定打乱顺序的三元组，请重建原始排列。

输入格式要求：
- 第一行为整数n
- 后续n-2行为三个空格分隔的整数

当前输入数据：
{input_example}

请输出任意满足条件的排列，格式为空格分隔的数字，并将最终答案放在[answer]标签内。例如：
[answer]1 2 3 4 5[/answer]"""  # 修复字符串结尾的引号对齐问题 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

