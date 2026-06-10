import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EplayingwithsuperglueInstructionGenerator(BaseInstructionGenerator):
    """Eplayingwithsuperglue Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, min_m=1, max_m=100):
        """
        初始化Eplayingwithsuperglue指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = max(min_n, 1)
        self.max_n = max(self.min_n, min(max_n, 100))  # Ensure max_n ≤ 100
        self.min_m = max(min_m, 1)
        self.max_m = max(self.min_m, min(max_m, 100))  # Ensure max_m ≤ 100
    
    def case_generator(self):
        # Generate valid board size
        while True:
            n = random.randint(self.min_n, self.max_n)
            m = random.randint(self.min_m, self.max_m)
            if n * m >= 2:
                break
        
        # Generate distinct positions
        while True:
            x1, y1 = random.randint(1, n), random.randint(1, m)
            x2, y2 = random.randint(1, n), random.randint(1, m)
            if (x1, y1) != (x2, y2):
                break
        
        return {
            'n': n,
            'm': m,
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = f"""Two players play a game on a {question_case['n']}x{question_case['m']} grid. Chips start at ({question_case['x1']},{question_case['y1']}) and ({question_case['x2']},{question_case['y2']}).

Rules:
1. First player moves one unglued chip (up/down/left/right) each turn
2. Second player places glue on an empty square each turn
3. First wins if chips meet, Second wins if both chips get glued

Determine the winner under optimal play. Put your final answer within [answer] tags, like [answer]First[/answer] or [answer]Second[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

