import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from fractions import Fraction
from math import isclose




class Koroperationunicode25cbInstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode25cb Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Koroperationunicode25cb指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.x = params.get('x', 1)
        self.y = params.get('y', 3)
    
    def case_generator(self):
        problem_type = random.choices(
            ['compute', 'solve_x', 'solve_xy', 'nested_solve'],
            weights=[5, 3, 1, 1],
            k=1
        )[0]

        if problem_type == 'compute':
            length = random.choice([2, 3])
            numbers = [random.randint(-5, 5) for _ in range(length)]
            return {
                "type": "compute",
                "expr": numbers,
                "answer": self._compute_chain(numbers)
            }

        elif problem_type == 'solve_x':
            eq_type = random.choice(["X○B=K", "A○X=K"])
            x, y = self.x, self.y
            
            if eq_type == "X○B=K":
                B = random.choice([n for n in range(-5,6) if n != 0])
                X1 = random.randint(-5, 5)
                K = (x*X1 + y*B) * (X1 + B)
                X2 = (-B*(x + y) - X1*y) // x
                return {
                    "type": "solve_x",
                    "equation": f"X○{B} = {K}",
                    "solutions": sorted([X1, X2])
                }
            else:
                A = random.randint(1, 5)
                X1 = random.randint(-5, 5)
                K = (x*A + y*X1) * (A + X1)
                X2 = Fraction(-A*(x + y) - x*A, y)
                return {
                    "type": "solve_x",
                    "equation": f"{A}○X = {K}",
                    "solutions": sorted([X1, float(X2)])
                }

        elif problem_type == 'solve_xy':
            x = random.randint(-3, 3)
            y = random.randint(-3, 3)
            equations = []
            for _ in range(2):
                while True:
                    A, B = random.randint(1,5), random.randint(1,5)
                    if (A + B) != 0:
                        break
                K = (A*x + B*y) * (A + B)
                equations.append(f"{A}○{B} = {K}")
            return {
                "type": "solve_xy",
                "equations": equations,
                "solution": (x, y)
            }

        elif problem_type == 'nested_solve':
            # 生成有效嵌套方程：A○(X○B)=C
            A = random.randint(1, 5)
            B = random.randint(1, 5)
            X = random.randint(-5, 5)
            
            # 计算内部表达式值
            inner_val = self._compute_op(X, B, self.x, self.y)
            # 计算最终结果C
            C = self._compute_op(A, inner_val, self.x, self.y)
            
            return {
                "type": "nested_solve",
                "equation": f"{A}○(X○{B}) = {C}",
                "solution": X,
                "params": (self.x, self.y),
                "B": B,
                "A": A
            }
    
    @staticmethod
    def prompt_func(case):
        if case['type'] == 'compute':
            expr = '○'.join(map(str, case['expr']))
            return (
                f"计算表达式：{expr}\n"
                "运算符○定义为：A○B = (xA + yB)(A + B)，其中x={x}，y={y}\n"
                "答案请用[[结果]]包裹，例如[[25]]"
            ).format(x=case.get('x',1), y=case.get('y',3))

        elif case['type'] == 'solve_x':
            return (
                f"解方程：{case['equation']}\n"
                "运算符○定义为：A○B = (xA + yB)(A + B)，其中x={x}，y={y}\n"
                "可能有多个解，答案格式：[[解1 or 解2]]\n"
                "支持分数（如5/3）和负数，示例：[[-3/2 or 4]]"
            ).format(x=case.get('x',1), y=case.get('y',3))

        elif case['type'] == 'solve_xy':
            return (
                "已知以下方程：\n" + 
                '\n'.join(case['equations']) + 
                "\n求参数x和y的值，答案格式：[[x=值,y=值]]"
            )

        elif case['type'] == 'nested_solve':
            return (
                f"解嵌套方程：{case['equation']}\n"
                "运算符○定义为：A○B = (xA + yB)(A + B)，其中x={x}，y={y}\n"
                "答案用[[数值]]包裹，示例：[[5]]"
            ).format(x=case['params'][0], y=case['params'][1]) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _compute_chain(self, numbers):
        res = numbers[0]
        for n in numbers[1:]:
            res = (self.x*res + self.y*n) * (res + n)
        return res

    @staticmethod
    def _compute_op(a, b, x, y):
        return (x*a + y*b) * (a + b)
