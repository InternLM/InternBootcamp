"""### 谜题描述
f■g=\frac{\partial f}{\partial x}+\frac{\partial g}{\partial x}.Example questions are as follows:

<example 0>
f(x,y)=x^2+y,g(x,y)=sinx+cosy, compute f■g.
Please provide your answer in LaTeX format. 
Wrap the final answer in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
f(x,y)=x^2+y,g(x,y)=3x+y^2, compute f■g.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
f(x,y)=sinx+y^2,g(x,y)=cosx-y, compute f■g.
Please provide your answer in LaTeX format. 
Wrap the final answer in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
f(x,y)=e^x,g(x,y)=x^3+y^3, compute f■g.
Please provide your answer in LaTeX format. 
Wrap the final answer in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
f(x,y)=x^2+xy,g(x,y)=2x+y, compute f■g.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
f(x,y)=sin^2(x)+y,g(x,y)=cos^2(x)+y, compute f■g.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
f(x,y)=x^2+y^2,g(x,y)=e^x+sin(y), compute f■g.
If there is a power inside the answer, write it in the form a^b (a is the base, b is the exponent).
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
f(x,y)=x^3+y^3,g(x,y)=x^2+y^2, compute f■g.
If there is a power inside the answer, write it in the form a^b (a is the base, b is the exponent).
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
f(x,y)=x⋅sin(y),g(x,y)=e^x+y^2,compute f■g.
Please provide your answer in LaTeX format. 
Wrap the final answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
f(x,y)=x/y,g(x,y)=x^3+y^3, compute f■g.
Please provide your answer in LaTeX format. 
Wrap the final answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
import sympy
from bootcamp import Basebootcamp

x, y = sympy.symbols('x y')

class KorOperationUnicode25a0bootcamp(Basebootcamp):
    def __init__(self, max_terms=3, max_degree=3, **kwargs):
        self.max_terms = max_terms
        self.max_degree = max_degree
        super().__init__(**kwargs)
    
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
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        solution = matches[-1].strip()
        # 清理多余空格和换行
        return re.sub(r'\s+', '', solution)
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 转换用户答案
            user_clean = solution.replace('\\', '').replace('{','').replace('}','')
            user_expr = sympy.parse_expr(user_clean, transformations='all')
            
            # 转换标准答案
            ans_expr = sympy.parse_expr(identity['_answer_sympy'])
            
            # 符号等价验证
            diff = sympy.simplify(user_expr - ans_expr)
            return diff.equals(0)
        except Exception as e:
            return False
