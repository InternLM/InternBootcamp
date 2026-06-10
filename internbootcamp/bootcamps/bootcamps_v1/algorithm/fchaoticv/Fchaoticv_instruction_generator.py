import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class FchaoticvInstructionGenerator(BaseInstructionGenerator):
    """Fchaoticv Bootcamp指令生成器"""
    
    def __init__(self, **kwargs):
        """
        初始化Fchaoticv指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        pass
    
    def case_generator(self):
        test_cases = [
            {'n': 3, 'k_list': [2, 1, 4], 'correct_answer': 5},
            {'n': 4, 'k_list': [3, 1, 4, 4], 'correct_answer': 6},
            {'n': 4, 'k_list': [3, 1, 4, 1], 'correct_answer': 6},
            {'n': 5, 'k_list': [3, 1, 4, 1, 5], 'correct_answer': 11},
            {'n': 2, 'k_list': [0, 0], 'correct_answer': 0},
            {'n': 1, 'k_list': [5], 'correct_answer': 3},
            {'n': 3, 'k_list': [3, 3, 3], 'correct_answer': 0},
            {'n': 2, 'k_list': [2, 5], 'correct_answer': 5},
            {'n': 4, 'k_list': [0, 1, 2, 3], 'correct_answer': 4},
        ]
        case = random.choice(test_cases)
        return case
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k_list = question_case['k_list']
        input_text = f"{n}\n{' '.join(map(str, k_list))}"
        prompt = f"""As Ivy, determine the optimal node P to minimize the total path length from all Vanessa's mind fragments in the ARC Library system. Each fragment is located at node k_i! (k_i factorial). Nodes form a tree where each node x (x>1) connects to x divided by its smallest prime divisor.

Input:
{input_text}

Output the minimal total path length as an integer. Enclose your answer within [answer] and [/answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

