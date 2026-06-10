import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class Koroperationunicode25b3RewardCalculator(BaseRewardCalculator):
    """Koroperationunicode25b3奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['correct_answer'].strip()
        solution = solution.strip()

        if identity['answer_format'] == 'latex':
            solution = re.sub(r'\s+', '', solution)
            expected = re.sub(r'\s+', '', expected)
            solution = solution.replace(r'\cdot', '').replace('*', '')
            expected = expected.replace(r'\cdot', '').replace('*', '')
        else:
            solution = solution.replace(' ', '')
            expected = expected.replace(' ', '')

        return solution == expected
    
    # 其他额外方法

