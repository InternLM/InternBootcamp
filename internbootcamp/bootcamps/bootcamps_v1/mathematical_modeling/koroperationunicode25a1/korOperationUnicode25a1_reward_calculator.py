import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class Koroperationunicode25a1RewardCalculator(BaseRewardCalculator):
    """Koroperationunicode25a1奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        problem_type = identity['problem_type']
        correct = identity['correct_answer']
        
        if problem_type == 'expression':
            return solution == correct
        else:
            try:
                num = round(float(solution), 4)
                return abs(num - correct) < 1e-4
            except:
                return False
    
    # 其他额外方法

