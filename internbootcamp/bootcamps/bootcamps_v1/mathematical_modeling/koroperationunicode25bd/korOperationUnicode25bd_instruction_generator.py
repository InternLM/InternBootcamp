import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import sympy as sp
import random




class Koroperationunicode25bdInstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode25bd Bootcamp指令生成器"""
    
    def __init__(self, x_value_prob=0.3, numeric_precision=4, **kwargs):
        """
        初始化Koroperationunicode25bd指令生成器
        
        Args:
            x_value_prob: 参数描述
            numeric_precision: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.x_value_prob = x_value_prob  # 数值问题的概率
        self.numeric_precision = numeric_precision
    
    def case_generator(self):
        f_expr, g_expr, g_double_prime, x_value = self.generate_case_components()
        
        # 生成两种问题类型
        is_numeric = random.random() < self.x_value_prob
        expected_str = None
        expected_num = None
        
        x = sp.symbols('x')
        correct_expr = f_expr + g_double_prime
        
        if is_numeric:
            # 数值计算
            numeric_value = correct_expr.subs(x, x_value).evalf()
            expected_num = round(float(numeric_value), self.numeric_precision)
        else:
            # 符号表达式处理
            expected_str = sp.latex(correct_expr.simplify())

        return {
            'f_latex': sp.latex(f_expr),
            'g_latex': sp.latex(g_expr),
            'x_value': x_value if is_numeric else None,
            'expected_num': expected_num,
            'expected_str': expected_str,
            'precision': self.numeric_precision,
            'is_numeric': is_numeric
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem = [
            "Solve the differential operator problem:",
            "Given:",
            f"f(x) = {question_case['f_latex']}",
            f"g(x) = {question_case['g_latex']}",
            "Compute: f▽g = f(x) + g''(x)"
        ]
        
        if question_case['is_numeric']:
            problem.append(f"at x = {question_case['x_value']}")
            problem.append(f"Provide a numerical value rounded to {question_case['precision']} decimal places.")
        else:
            problem.append("Provide the result as a LaTeX mathematical expression.")
        
        problem.append("Format your answer within double square brackets: [[answer]]")
        return '\n'.join(problem) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def safe_generate(self, func_type):
        """生成定义域安全的函数表达式"""
        x = sp.symbols('x')

        # 控制函数生成范围
        if func_type == 'logarithm':
            base = random.choice([sp.E, 10])
            return random.randint(1,3)*sp.log(base**random.randint(1,3)*x)
        elif func_type == 'polynomial':
            return sum(random.randint(1,3)*x**i for i in range(3))
        elif func_type == 'trigonometric':
            choice = random.choice([sp.sin, sp.cos])
            return random.randint(1,3)*choice(random.randint(1,3)*x)
        else:  # 指数函数
            return random.randint(1,3)*sp.exp(random.randint(1,3)*x)

    def generate_case_components(self):
        """生成合法的问题组件"""
        x = sp.symbols('x')
        for _ in range(100):  # 尝试次数限制
            # 控制函数类型组合
            f_type = random.choice(['polynomial', 'trigonometric', 'exponential'])
            g_type = random.choice(['polynomial', 'trigonometric', 'logarithm'])

            f_expr = self.safe_generate(f_type)
            g_expr = self.safe_generate(g_type)

            # 计算二阶导数
            try:
                g_double_prime = sp.diff(g_expr, x, 2)
            except:
                continue

            # 生成合法的x值
            x_value = self.find_valid_x(f_expr, g_expr)
            if x_value is None:
                continue

            return f_expr, g_expr, g_double_prime, x_value

        # 保底返回
        return x, sp.sin(x), 0, 1.0

    def find_valid_x(self, f_expr, g_expr):
        """寻找满足所有条件的x值"""
        x = sp.symbols('x')
        for _ in range(100):
            # 根据函数类型调整取值范围
            if any(func.has(sp.log(x)) for func in [g_expr]):
                x_candidate = random.uniform(0.1, 5)
            else:
                x_candidate = random.uniform(-3, 3)

            try:
                f_expr.subs(x, x_candidate)
                g_expr.subs(x, x_candidate)
                return round(x_candidate, 2)
            except:
                continue
        return None
