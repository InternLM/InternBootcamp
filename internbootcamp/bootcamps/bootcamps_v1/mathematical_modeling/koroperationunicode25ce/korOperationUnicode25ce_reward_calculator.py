import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class Koroperationunicode25ceRewardCalculator(BaseRewardCalculator):
    """Koroperationunicode25ce奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[([^\[\]]+)\]\]', output)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if identity['type'] == 'calculation':
                real, imag = cls.parse_complex(solution)
                return real == identity['correct'][0] and imag == identity['correct'][1]
            else:
                X = int(solution)
                params = identity['params']
                
                if identity['x_pos'] == 'left':
                    a, b, c, op = params
                    left_real, left_imag = cls.compute_operator(X, a)
                    right_real, right_imag = cls.compute_operator(b, c)
                elif identity['x_pos'] == 'right':
                    a, b, c, op = params
                    right_real, right_imag = cls.compute_operator(X, a)
                    left_real, left_imag = cls.compute_operator(b, c)
                elif identity['x_pos'] == 'left_scalar':
                    a, b, c, scalar, op = params
                    left_real, left_imag = cls.compute_operator(X, a)
                    right_real, right_imag = cls.compute_operator(b, c)
                    right_real *= scalar
                    right_imag *= scalar
                elif identity['x_pos'] == 'right_scalar':
                    a, b, c, scalar, op = params
                    right_real, right_imag = cls.compute_operator(X, a)
                    right_real *= scalar
                    right_imag *= scalar
                    left_real, left_imag = cls.compute_operator(b, c)
                
                if identity.get('form', '').split()[1] == '+':
                    total_real = left_real + right_real
                    total_imag = left_imag + right_imag
                else:
                    total_real = left_real - right_real
                    total_imag = left_imag - right_imag
                
                return (total_real == identity['target'][0] and 
                        total_imag == identity['target'][1])
        except:
            return False
    
    # 其他额外方法

