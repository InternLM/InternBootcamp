"""### 谜题描述
a●b=\int_{a}^{b} f(x) \, dx+6.Example questions are as follows:

<example 0>
Given f(x)=2x, compute 1●3.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
Given f(x)=sin(x), compute 0●π.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
Given f(x)=x^2, compute 0●2.
If the answer is a fraction, write it in 'a/b' text format. Decimals are not allowed.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
Given f(x)=1/x, compute 1●e.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
Given f(x)=x^3, compute -1●1.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
Given f(x)=cos(x), Compute 0●π/2.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
Given f(x)=x-1, compute -2●2.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
Given f(x)=x a★3=10, find a.
If there is more than one answer, please separate them with 'or',e.g.[[1or2]].
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
Given f(x)=1/x 1★a=ln(2)+6, find a.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
Given f(x)=x^3 a★1=6, find a.
The answer may be negative, if so write it in a format such as '-5'.
If there is more than one answer, please separate them with 'or',e.g.[[1or2]].
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
import sympy as sp
from sympy.abc import x, a, b
from bootcamp import Basebootcamp

class KorOperationUnicode25cfbootcamp(Basebootcamp):
    def __init__(self, **params):
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

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        if not matches:
            return None
            
        last_match = matches[-1].strip()
        solutions = []
        for part in last_match.split('or'):
            part = part.strip()
            try:
                if '/' in part:
                    numerator, denominator = map(int, part.split('/'))
                    solutions.append(numerator / denominator)
                else:
                    solutions.append(float(part))
            except:
                continue
        return solutions if len(solutions) > 1 else solutions[0] if solutions else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        if identity['problem_type'] == 'compute':
            return abs(solution - identity['correct_answer']) < 1e-6
        else:
            correct_set = {round(c, 6) for c in identity['correct_answers']}
            user_sols = [solution] if not isinstance(solution, list) else solution
            user_set = {round(s, 6) for s in user_sols}
            return correct_set == user_set

    # Helper methods with type safety
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
