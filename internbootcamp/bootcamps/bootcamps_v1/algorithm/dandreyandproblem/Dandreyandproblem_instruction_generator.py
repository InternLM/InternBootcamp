import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DandreyandproblemInstructionGenerator(BaseInstructionGenerator):
    """Dandreyandproblem Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, precision=1e-12, **kwargs):
        """
        初始化Dandreyandproblem指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            precision: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_n = min_n
        self.max_n = max_n
        self.precision = precision
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        probs = [
            float(f"{random.uniform(0.0, 1.0):.6f}")  # 确保精确的6位小数
            for _ in range(n)
        ]
        return {
            'n': n,
            'probs': probs,
            'correct_answer': self.compute_max_prob(probs)
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        probs = question_case['probs']
        return (
            "Andrey needs to select friends to maximize the probability of getting exactly one problem.\n\n"
            "Problem Rules:\n"
            "1. Choose a subset of friends to ask\n"
            "2. The probability of success is calculated for exactly one friend succeeding\n"
            "3. Output must have at least 9 decimal places\n\n"
            f"Input:\n{question_case['n']}\n{' '.join(f'{p:.6f}' for p in probs)}\n\n"
            "Output format:\n[answer]probability[/answer]\n"
            "Example: [answer]0.260000000000[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_max_prob(probs):
        sorted_probs = sorted(probs, reverse=True)
        max_prob = 0.0
        product_inverse = 1.0
        current_prob = 0.0

        for p in sorted_probs:
            candidate = (1 - p)*current_prob + p*product_inverse
            if candidate > max_prob + 1e-15:  # 防止浮点误差误判
                max_prob = candidate
                product_inverse *= (1 - p)
                current_prob = max_prob
            else:
                break
        return max_prob
