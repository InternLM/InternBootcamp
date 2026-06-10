import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import sympy as sp
from sympy.abc import x
from sympy.abc import a
from sympy.abc import b




class Koroperationunicode25cfRewardCalculator(BaseRewardCalculator):
    """Koroperationunicode25cf奖励计算器"""
    
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
    
    # 其他额外方法

