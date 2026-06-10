import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import sympy as sp
import random




class Koroperationunicode25bdRewardCalculator(BaseRewardCalculator):
    """Koroperationunicode25bd奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if identity['is_numeric']:
                # 数值验证
                user_val = round(float(solution), identity['precision'])
                return abs(user_val - identity['expected_num']) < 1e-6
            else:
                # 符号验证
                x = sp.symbols('x')
                user_expr = sp.sympify(solution, evaluate=False)
                expected_expr = sp.sympify(identity['expected_str'], evaluate=False)
                return sp.simplify(user_expr - expected_expr) == 0
        except:
            return False
    
    # 其他额外方法

