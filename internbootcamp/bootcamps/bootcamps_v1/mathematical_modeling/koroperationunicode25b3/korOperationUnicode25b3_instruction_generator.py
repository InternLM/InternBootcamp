import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import sympy
from sympy import symbols
from sympy import diff
from sympy import exp
from sympy import log
from sympy import sin
from sympy import cos
from sympy import sqrt
from sympy import pi
from sympy import simplify
from sympy import Rational

# === 源文件中的全局变量 ===

x = symbols('x')


class Koroperationunicode25b3InstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode25b3 Bootcamp指令生成器"""
    
    def __init__(self, max_degree=3, allow_x_value=True):
        """
        初始化Koroperationunicode25b3指令生成器
        
        Args:
            max_degree: 参数描述
            allow_x_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_degree = max_degree
        self.allow_x_value = allow_x_value
    
    def case_generator(self):
        f_expr = self.generate_function()
        g_expr = self.generate_function()

        h = f_expr.subs(x, g_expr)
        h_prime = diff(h, x)

        x_value, correct_answer, answer_format = None, None, 'latex'

        if self.allow_x_value and random.random() < 0.2:
            for candidate in [1, 2, pi/2, pi]:
                try:
                    g_val = g_expr.subs(x, candidate)
                    if not (g_val.is_real and g_val.is_finite):
                        continue
                    h_prime_val = h_prime.subs(x, candidate)
                    if not (h_prime_val.is_real and h_prime_val.is_finite):
                        continue

                    simplified = simplify(h_prime_val)
                    if simplified.is_Integer:
                        correct_answer = f"{int(simplified)}"
                        answer_format = 'integer'
                    elif isinstance(simplified, Rational):
                        correct_answer = f"{simplified.p}/{simplified.q}"
                        answer_format = 'fraction'
                    else:
                        num_val = float(simplified.evalf())
                        correct_answer = f"{num_val:.2f}"
                        answer_format = 'float'
                    x_value = candidate
                    break
                except:
                    continue

        if correct_answer is None:
            correct_answer = sympy.latex(simplify(h_prime))
            answer_format = 'latex'

        case = {
            'f': sympy.latex(f_expr),
            'g': sympy.latex(g_expr),
            'x_value': sympy.latex(x_value) if x_value is not None else None,
            'correct_answer': correct_answer,
            'answer_format': answer_format
        }
        return case
    
    @staticmethod
    def prompt_func(question_case):
        f = question_case['f']
        g = question_case['g']
        x_val = question_case['x_value']
        fmt = question_case['answer_format']

        problem = f"f(x) = {f}, g(x) = {g}. Compute f△g."
        if x_val is not None:
            problem = f"f(x) = {f}, g(x) = {g}. Find f△g at x = {x_val}."

        format_rules = {
            'latex': "Provide your answer in LaTeX enclosed in [[ ]].",
            'fraction': "Write fractions as 'a/b' within [[ ]].",
            'integer': "Provide an integer within [[ ]].",
            'float': "Round to two decimal places within [[ ]]."
        }.get(fmt, "Place your answer within [[ ]].")

        return f"""Define that: f△g=(f(g(x)))′

Solve the calculus puzzle:

**Problem**: {problem}

**Rules**:
- Compute the derivative of f(g(x)).
{f"Substitute x = {x_val}." if x_val else ""}
- {format_rules}

**Answer**: [[your answer here]]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_function(self):
        func_types = ['poly', 'sin', 'cos', 'exp', 'ln', 'sqrt']
        func_type = random.choice(func_types)

        if func_type == 'poly':
            degree = random.randint(1, self.max_degree)
            expr = x**degree
        elif func_type == 'sin':
            expr = sin(x)
        elif func_type == 'cos':
            expr = cos(x)
        elif func_type == 'exp':
            expr = exp(x)
        elif func_type == 'ln':
            expr = log(x)
        elif func_type == 'sqrt':
            expr = sqrt(x)

        if random.random() < 0.5:
            expr *= x**random.randint(1, 2)
        return expr
