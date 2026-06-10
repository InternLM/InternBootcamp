import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CbasketballexerciseInstructionGenerator(BaseInstructionGenerator):
    """Cbasketballexercise Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cbasketballexercise指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = params.get('n_min', 1)
        self.n_max = params.get('n_max', 10)
        self.h_min = params.get('h_min', 1)
        self.h_max = params.get('h_max', 10**9)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        h1 = [random.randint(self.h_min, self.h_max) for _ in range(n)]
        h2 = [random.randint(self.h_min, self.h_max) for _ in range(n)]
        return {
            'n': n,
            'h1': h1,
            'h2': h2
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        h1 = question_case['h1']
        h2 = question_case['h2']
        prompt = (
            f"现在有两排学生，每排有{n}个学生。第一排的身高依次为：{h1}。第二排的身高依次为：{h2}。\n"
            "根据规则，Demid需要选择一个队，使得总身高最大。规则如下：\n"
            "1. 每次选择的学生必须来自另一排，不能连续选同一排。\n"
            "2. 学生的索引必须严格递增，即只能选择当前选中的学生右边的学生。\n"
            "3. 第一个选的学生可以是任意一排的任意位置。\n"
            "请计算 Demid 能选择的最大总身高，并将答案放在[answer]标签中，例如：\n"
            "[answer]29[/answer]\n"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

