import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CtreesInstructionGenerator(BaseInstructionGenerator):
    """Ctrees Bootcamp指令生成器"""
    
    def __init__(self, max_n=100, max_height=100):
        """
        初始化Ctrees指令生成器
        
        Args:
            max_n: 参数描述
            max_height: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_height = max_height
    
    def case_generator(self):
        # 增强案例生成逻辑，增加边界条件覆盖
        n = random.choice([
            1, 2, 3, 
            self.max_n, 
            random.randint(4, self.max_n)
        ]) if self.max_n > 4 else random.randint(1, self.max_n)
        
        # 随机生成时需要确保至少存在一个合法解
        while True:
            heights = [random.randint(1, self.max_height) for _ in range(n)]
            valid_heights = [
                h - min(i, n-1-i)
                for i, h in enumerate(heights)
                if h > min(i, n-1-i)
            ]
            if valid_heights or n == 0:
                break
                
        correct_answer = self._calculate_correct_answer(n, heights)
        return {
            'n': n,
            'heights': heights,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""As a city planner in Bertown, you need to adjust {question_case['n']} trees with heights {question_case['heights']} to form a beautiful sequence. The sequence must satisfy:
1. Symmetric pairs (k-th from start and end must be equal)
2. Each inward pair increases by exactly 1 meter
3. All heights remain positive (>0)

Calculate the minimal trees to modify. Format your answer as: [answer]number[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_correct_answer(n, heights):
        m = [min(i, n-1 -i) for i in range(n)]
        adjusted = [h - mi for h, mi in zip(heights, m)]
        counter = {}
        for val in adjusted:
            if val > 0:
                counter[val] = counter.get(val, 0) + 1

        max_freq = max(counter.values()) if counter else 0
        return n - max_freq
