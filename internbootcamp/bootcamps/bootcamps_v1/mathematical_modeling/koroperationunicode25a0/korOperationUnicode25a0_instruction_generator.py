import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import sympy

# === 源文件中的全局变量 ===

x, y = sympy.symbols('x y')


class Koroperationunicode25a0InstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode25a0 Bootcamp指令生成器"""
    
    def __init__(self, max_terms=3, max_degree=3, **kwargs):
        """
        初始化Koroperationunicode25a0指令生成器
        
        Args:
            max_terms: 参数描述
            max_degree: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_terms = max_terms
        self.max_degree = max_degree
        super().__init__(**kwargs)
    
    def case_generator(self):
        while True:
            try:
                f_expr = self._generate_expression()
                g_expr = self._generate_expression()
                
                df_dx = sympy.diff(f_expr, x)
                dg_dx = sympy.diff(g_expr, x)
                ans_expr = sympy.simplify(df_dx + dg_dx)
                
                # 过滤无效表达式
                if ans_expr.is_number:
                    continue
                    
                return {
                    'f_latex': sympy.latex(f_expr),
                    'g_latex': sympy.latex(g_expr),
                    '_f_sympy': str(f_expr),
                    '_g_sympy': str(g_expr),
                    '_answer_sympy': str(ans_expr)
                }
            except:
                continue
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""请计算以下函数的偏导数之和：
        
给定：
$$f(x, y) = {question_case['f_latex']}$$
$$g(x, y) = {question_case['g_latex']}$$

其中运算符■定义为：
$$f■g = \\frac{{\\partial f}}{{\\partial x}} + \\frac{{\\partial g}}{{\\partial x}}$$

要求：
1. 结果必须使用LaTeX公式表示
2. 指数使用^符号（如x²写作x^2）
3. 分式使用\\frac{{分子}}{{分母}}格式
4. 将最终答案包裹在双方括号中，例如：[[2x + \\cos x]]

请直接给出最终答案：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_term(self):
        term_types = [
            # 多项式项
            lambda: x**random.randint(1, self.max_degree),
            lambda: y**random.randint(1, self.max_degree),
            # 三角函数
            lambda: sympy.sin(random.choice([x, y])),
            lambda: sympy.cos(random.choice([x, y])),
            # 指数函数
            lambda: sympy.exp(x),
            # 分式项
            lambda: sympy.Mul(
                sympy.Poly(random.randint(1, 3)*x**random.randint(0,2), x), 
                sympy.Pow(y, -random.randint(1,2)), 
                evaluate=False
            ),
            # 常数项
            lambda: sympy.Integer(random.randint(1, 5))
        ]
        return random.choice(term_types)()

    def _generate_expression(self):
        num_terms = random.randint(1, self.max_terms)
        expr = sympy.Integer(0)
        for _ in range(num_terms):
            term = self._generate_term()
            # 确保不生成全零表达式
            if expr == 0:
                expr = term
            else:
                expr += term
        return expr
