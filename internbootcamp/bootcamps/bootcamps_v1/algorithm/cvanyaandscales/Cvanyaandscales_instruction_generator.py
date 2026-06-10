import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CvanyaandscalesInstructionGenerator(BaseInstructionGenerator):
    """Cvanyaandscales Bootcamp指令生成器"""
    
    def __init__(self, w_min=2, w_max=10**9, m_min=1, m_max=10**9):
        """
        初始化Cvanyaandscales指令生成器
        
        Args:
            w_min: 参数描述
            w_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.w_min = w_min
        self.w_max = w_max
        self.m_min = m_min
        self.m_max = m_max
    
    def case_generator(self):
        w = random.randint(self.w_min, self.w_max)
        m = random.randint(self.m_min, self.m_max)
        return {'w': w, 'm': m}
    
    @staticmethod
    def prompt_func(question_case):
        w = question_case['w']
        m = question_case['m']
        prompt = f"""Vanya has a balance scale and weights in denominations of w⁰, w¹, ..., w¹⁰⁰ grams (w is an integer ≥2). Determine if you can measure an object of mass {m}g by:
- Placing the object on the left pan
- Placing some weights on either pan
such that the total weight on both pans is equal.

Output 'YES' or 'NO' enclosed in [answer] tags. Example: [answer]YES[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def check_balance(w, m):
        if w < 2 or m < 1:
            return "NO"

        # Convert m to base-w digits
        current_m = m
        dig = []
        while current_m > 0:
            dig.append(current_m % w)
            current_m //= w

        # Process digits with dynamic padding
        dig += [0] * (len(dig) + 2)  # Ensure sufficient padding

        for i in range(len(dig)):
            if dig[i] > 1:
                # Dynamically extend array if needed
                while i + 1 >= len(dig):
                    dig.append(0)

                diff = dig[i] - w
                if diff < -1:
                    return "NO"

                dig[i] = diff
                dig[i+1] += 1

        # Final validation check
        return "YES" if all(d in (0, 1) for d in dig) else "NO"
