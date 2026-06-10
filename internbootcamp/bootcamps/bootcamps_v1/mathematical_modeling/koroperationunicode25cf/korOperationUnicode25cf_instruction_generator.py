import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import sympy as sp
from sympy.abc import x
from sympy.abc import a
from sympy.abc import b




class Koroperationunicode25cfInstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode25cf Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Koroperationunicode25cf指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.operator_symbols = params.get('operator_symbols', ['●', '★', '◆'])
        self.compute_prob = params.get('compute_prob', 0.7)
        self.function_list = params.get('function_list', [
            'm*x', 'x**n', 'sin(x)', 'cos(x)', '1/x'
        ])
        self.default_a_range = params.get('a_range', (-5, 5))
        self.default_b_range = params.get('b_range', (-5, 5))
    
    def case_generator(self):
        if random.random() < self.compute_prob:
            return self._generate_compute_case()
        else:
            return self._generate_solve_case()
    
    @staticmethod
    def prompt_func(question_case):
        operator = question_case['operator']
        if question_case['problem_type'] == 'compute':
            return (
                f"Given f(x) = {question_case['f']}, compute {question_case['a']}{operator}{question_case['b']}.\n"
                f"The operation a{operator}b is defined as ∫_a^b f(x)dx + 6. "
                "Calculate the result. For fractions, use 'a/b' format. "
                "Put your answer in [[ ]]."
            )
        else:
            return (
                f"Given f(x) = {question_case['f']}, {question_case['target_var']}{operator}{question_case['known_value']} = {question_case['result']}. "
                f"Find {question_case['target_var']}.\n"
                f"The operation a{operator}b is defined as ∫_a^b f(x)dx + 6. "
                "For multiple answers, separate with 'or'. Use fractions if needed. "
                "Put your answer in [[ ]]."
            ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_compute_case(self):
        func_info = self._generate_random_function()
        f_expr, f_str = func_info['expr'], func_info['str']

        if func_info['str'] == '1/x':
            a_val, b_val = self._generate_valid_interval_for_reciprocal()
        else:
            a_val, b_val = self._generate_valid_interval()

        integral = sp.integrate(f_expr, (x, a_val, b_val))
        result = self._safe_eval(integral + 6)

        return {
            'problem_type': 'compute',
            'f': f_str,
            'a': a_val,
            'b': b_val,
            'operator': random.choice(self.operator_symbols),
            'correct_answer': result
        }

    def _generate_solve_case(self):
        func_info = self._generate_random_function(solve_case=True)
        f_expr, f_str = func_info['expr'], func_info['str']
        target_var = random.choice(['a', 'b'])
        known_var = 'b' if target_var == 'a' else 'a'

        # Handle special case for 1/x
        if f_str == '1/x':
            sign_constraint = 'positive'
        else:
            sign_constraint = None

        if target_var == 'a':
            b_val = self._generate_value(exclude_zero=f_str == '1/x', sign=sign_constraint)
            a_sample = self._generate_value(exclude=b_val, sign=sign_constraint)
        else:
            a_val = self._generate_value(exclude_zero=f_str == '1/x', sign=sign_constraint)
            b_sample = self._generate_value(exclude=a_val, sign=sign_constraint)

        # Generate equation with explicit result value
        simple_case = func_info.get('simple', False)
        result_val = random.randint(5, 15) if simple_case else random.randint(3, 20)

        if target_var == 'a':
            integral = sp.integrate(f_expr, (x, sp.Symbol('a'), b_val))
        else:
            integral = sp.integrate(f_expr, (x, a_val, sp.Symbol('b')))

        equation = integral + 6 - result_val

        solutions = self._solve_equation(equation, target_var)
        if not solutions:
            return self.case_generator()

        return {
            'problem_type': 'solve',
            'f': f_str,
            'known_var': known_var,
            'known_value': b_val if target_var == 'a' else a_val,
            'target_var': target_var,
            'operator': random.choice(self.operator_symbols),
            'result': result_val,  # Add result field
            'correct_answers': solutions
        }

    def _generate_random_function(self, solve_case=False):
        func_type = random.choice(self.function_list)
        params = {}

        if func_type == 'm*x':
            params['m'] = random.choice([-2, -1, 1, 2, 3])
            return {'expr': params['m']*x, 'str': f"{params['m']}x", 'simple': True}
        elif func_type == 'x**n':
            params['n'] = random.randint(2, 3) if solve_case else random.randint(2, 4)
            return {'expr': x**params['n'], 'str': f"x^{params['n']}"}
        elif func_type == '1/x':
            return {'expr': 1/x, 'str': "1/x"}
        elif func_type in ('sin(x)', 'cos(x)'):
            return {'expr': sp.__dict__[func_type[:3]](x), 'str': func_type}
        raise ValueError("Invalid function type")

    def _generate_valid_interval(self):
        while True:
            a_val = random.randint(*self.default_a_range)
            b_val = random.randint(*self.default_b_range)
            if a_val != b_val:
                return (a_val, b_val) if a_val < b_val else (b_val, a_val)

    def _generate_valid_interval_for_reciprocal(self):
        while True:
            # Ensure same sign and non-zero
            if random.choice([True, False]):
                a_val = random.randint(1, self.default_a_range[1])
                b_val = random.randint(1, self.default_b_range[1])
            else:
                a_val = random.randint(self.default_a_range[0], -1)
                b_val = random.randint(self.default_b_range[0], -1)
            if a_val != b_val:
                return (a_val, b_val) if a_val < b_val else (b_val, a_val)

    def _generate_value(self, exclude=None, exclude_zero=False, sign=None):
        while True:
            val = random.randint(*self.default_a_range)
            if sign == 'positive' and val <= 0:
                continue
            if sign == 'negative' and val >= 0:
                continue
            if exclude_zero and val == 0:
                continue
            if val == exclude:
                continue
            return val

    def _solve_equation(self, equation, target_var):
        symbol = sp.Symbol(target_var)
        try:
            solutions = sp.solve(equation, symbol)
            real_solutions = [sol.evalf() for sol in solutions if sol.is_real]
            return list({round(float(sol), 6) for sol in real_solutions if sol.is_real})
        except:
            return []

    @staticmethod
    def _safe_eval(expr):
        try:
            return float(expr.evalf())
        except:
            return float(expr)
