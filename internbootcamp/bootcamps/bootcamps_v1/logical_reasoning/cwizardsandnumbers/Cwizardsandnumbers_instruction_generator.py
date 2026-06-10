import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from functools import lru_cache




class CwizardsandnumbersInstructionGenerator(BaseInstructionGenerator):
    """Cwizardsandnumbers Bootcamp指令生成器"""
    
    def __init__(self, a_min=0, a_max=10**5, b_min=0, b_max=10**5):
        """
        初始化Cwizardsandnumbers指令生成器
        
        Args:
            a_min: 参数描述
            a_max: 参数描述
            b_min: 参数描述
            b_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.a_min = a_min
        self.a_max = a_max
        self.b_min = b_min
        self.b_max = b_max
    
    def case_generator(self):
        a = random.randint(self.a_min, self.a_max)
        b = random.randint(self.b_min, self.b_max)
        a, b = sorted((a, b))
        correct_answer = 'First' if self.is_first_win(a, b) else 'Second'
        return {
            'a': a,
            'b': b,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        a = question_case['a']
        b = question_case['b']
        prompt = f"两个巫师在玩一个数字游戏。黑板上写着两个数a={a}和b={b}。玩家轮流进行以下操作：\n"
        prompt += "1. 将较大的数减去较小的数的k倍（k>0，结果不能为负）。\n"
        prompt += "2. 将较大的数对较小的数取模。\n"
        prompt += "无法进行操作的玩家输。轮到你时，作为先手，你会赢吗？\n"
        prompt += "请判断先手会赢还是输，输出'First'表示先手赢，'Second'表示先手输。请将答案放在[answer]标签中，例如：[answer]First[/answer]\n"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    @lru_cache(maxsize=None)
    def is_first_win(a, b):
        if a == 0:
            return False
        if not Cwizardsandnumbersbootcamp.is_first_win(b % a, a):
            return True
        ans = b // a
        ans %= a + 1
        ans %= 2
        return ans % 2 == 0
