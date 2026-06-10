import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from fractions import Fraction
from math import isclose




class Koroperationunicode25cbRewardCalculator(BaseRewardCalculator):
    """Koroperationunicode25cb奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        patterns = [
            # 参数解
            r'\[\[x\s*=\s*(-?\d+)\s*,\s*y\s*=\s*(-?\d+)\]\]',
            # 带分数/根号的多解
            r'\[\[((?:-?\d+/\d+|\d+|-\d+|\\sqrt{\d+})(?:\s+or\s+[-?\d+/\d+|\d+|\\sqrt{\d+}]+)+)\]\]',
            # 单值解
            r'\[\[(-?\d+/\d+|\d+|-\d+|\\sqrt{\d+})\]\]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                last_match = matches[-1]
                if isinstance(last_match, tuple):
                    return f"x={last_match[0]},y={last_match[1]}"
                return last_match
        return None
    
    @classmethod
    def _verify_correction(cls, answer, case):
        try:
            if case['type'] == 'compute':
                return int(answer) == case['answer']
            
            elif case['type'] == 'solve_x':
                expected = set(case['solutions'])
                # 解析答案
                parts = answer.split(' or ')
                solutions = []
                for p in parts:
                    if '/' in p:
                        solutions.append(float(Fraction(p)))
                    elif 'sqrt' in p:
                        solutions.append(eval(p.replace('\\sqrt', 'math.sqrt'))) 
                    else:
                        solutions.append(float(p))
                # 允许浮点误差
                return all(any(isclose(s, e, rel_tol=1e-9) for e in expected) for s in solutions) and len(solutions) == len(expected)
            
            elif case['type'] == 'solve_xy':
                x = int(re.search(r'x=(-?\d+)', answer).group(1))
                y = int(re.search(r'y=(-?\d+)', answer).group(1))
                return (x, y) == case['solution']
            
            elif case['type'] == 'nested_solve':
                X = float(answer)
                # 验证嵌套计算
                inner = cls._compute_op(X, case['B'], *case['params'])
                final = cls._compute_op(case['A'], inner, *case['params'])
                return isclose(final, int(case['equation'].split('=')[-1]), rel_tol=1e-9)
            
            return False
        except:
            return False
    
    # 其他额外方法

