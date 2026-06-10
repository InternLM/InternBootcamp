import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import sympy as sp
import random
import math

# === 源文件中的全局变量 ===

x = sp.symbols('x')

base_functions = [
    'x**2',
    'x**3',
    'sin(x)',
    'cos(x)',
    'exp(x)',
    'ln(x)',
    'sqrt(x)',
    'tan(x)',
    'x',
]


class Koroperationunicode25a1InstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode25a1 Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Koroperationunicode25a1指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params.get('params', {})
        self.prob_evaluate = self.params.get('prob_evaluate', 0.5)
        self.x_candidates = self.params.get('x_candidates', [0, 1, 2, math.pi/4, math.pi/2, math.pi])
    
    def case_generator(self):
        f_str = random.choice(base_functions)
        g_str = random.choice(base_functions)
        
        f_expr = sp.parse_expr(f_str)
        g_expr = sp.parse_expr(g_str)
        
        df = f_expr.diff(x)
        dg = g_expr.diff(x)
        answer_expr = df + dg
        
        answer_latex = sp.latex(answer_expr, mul_symbol=None)
        
        problem_type = 'expression'
        correct_answer = answer_latex
        x_value = None
        
        if random.random() < self.prob_evaluate:
            max_attempts = 5
            for _ in range(max_attempts):
                x_val = random.choice(self.x_candidates)
                try:
                    value = answer_expr.subs(x, x_val).evalf()
                    if value.is_real and not value.has(sp.nan, sp.zoo, sp.oo):
                        correct_answer = round(float(value), 4)
                        problem_type = 'evaluate'
                        x_value = x_val
                        break
                except:
                    continue
        
        case = {
            'f': sp.latex(f_expr, mul_symbol=None),
            'g': sp.latex(g_expr, mul_symbol=None),
            'problem_type': problem_type,
            'correct_answer': correct_answer,
            'x_value': x_value
        }
        return case
    
    @staticmethod
    def prompt_func(question_case) -> str:
        f = question_case['f']
        g = question_case['g']
        x_val = question_case['x_value']
        problem_type = question_case['problem_type']
        
        prompt = [
            "You are a calculus expert. Solve the problem using the following rules:",
            "The operation f□g is defined as f'(x) + g'(x), where f' and g' are derivatives with respect to x.",
            "",
            f"Given:",
            f"f(x) = {f}",
            f"g(x) = {g}",
            ""
        ]
        
        if problem_type == 'evaluate':
            prompt.append(f"Find the numerical value of f□g at x = {x_val}.")
            prompt.append("Provide a single number within [[ ]].")
        else:
            prompt.append("Compute the expression for f□g.")
            prompt.append("Present your answer in LaTeX within [[ ]].")
        
        prompt.append("Example: [[2x + \\cos(x)]] or [[3.14]]")
        return '\n'.join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

