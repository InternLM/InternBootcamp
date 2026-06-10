import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CmemoryanddeevolutionInstructionGenerator(BaseInstructionGenerator):
    """Cmemoryanddeevolution Bootcamp指令生成器"""
    
    def __init__(self, min_y=3, max_x=100000):
        """
        初始化Cmemoryanddeevolution指令生成器
        
        Args:
            min_y: 参数描述
            max_x: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_y = min_y
        self.max_x = max_x
    
    def case_generator(self):
        y = random.randint(self.min_y, self.max_x - 1)
        x = random.randint(y + 1, self.max_x)
        return {'x': x, 'y': y}
    
    @staticmethod
    def prompt_func(question_case):
        x = question_case['x']
        y = question_case['y']
        prompt = f"""Memory starts with an equilateral triangle with side length {x} and wants to transform it into one with side length {y}. Each second, he can modify one side's length to any positive integer, provided the new triangle remains non-degenerate (sum of any two sides exceeds the third). All side lengths must be integers. What is the minimum number of seconds required?

Output the answer as an integer enclosed within [answer] and [/answer]. Example: [answer]4[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

