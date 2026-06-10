import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CnewyearratingschangeInstructionGenerator(BaseInstructionGenerator):
    """Cnewyearratingschange Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cnewyearratingschange指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = params.get('n_min', 1)
        self.n_max = params.get('n_max', 100)
        self.a_min = params.get('a_min', 1)
        self.a_max = params.get('a_max', 10**5)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        a = [random.randint(self.a_min, self.a_max) for _ in range(n)]
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        problem_text = (
            "你是一个网站的管理员，需要为每个用户分配唯一的评分作为新年礼物。每个用户希望获得至少a_i的评分。所有评分必须唯一且总和最小。\n\n"
            "输入格式：\n"
            "- 第一行是整数n，表示用户数。\n"
            "- 第二行是n个整数a_1 a_2 ... a_n，表示每个用户的最小需求。\n\n"
            "输出格式：\n"
            "- 输出n个整数b_1 b_2 ... b_n，满足b_i ≥ a_i、所有b_i唯一且总和最小。\n\n"
            "示例输入：\n3\n5 1 1\n示例输出：\n5 1 2\n\n"
            f"当前输入：\n{n}\n{' '.join(map(str, a))}\n"
            "请将答案放在[answer]和[/answer]之间，例如：[answer]1 2 3[/answer]"
        )
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

