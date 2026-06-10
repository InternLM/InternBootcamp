import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from itertools import permutations




class KorpuzzlecryptomathRewardCalculator(BaseRewardCalculator):
    """Korpuzzlecryptomath奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        if not matches:
            return None
        
        solution = {}
        for pair in matches[-1].split(','):
            pair = pair.strip()
            if '=' not in pair:
                continue
            letter, value = pair.split('=', 1)
            letter = letter.strip().upper()
            try:
                num = int(value.strip())
                if 0 <= num <= 9:
                    solution[letter] = num
            except ValueError:
                continue
        return solution if solution else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        equation = identity["equation"]
        try:
            left, right = equation.split('=')
            terms = left.split('+')
            sum_terms = 0
            for term in terms:
                if len(term) > 1 and solution[term[0]] == 0:
                    return False
                sum_terms += int(''.join(str(solution[c]) for c in term))
            
            result = right.strip()
            if len(result) > 1 and solution[result[0]] == 0:
                return False
            result_num = int(''.join(str(solution[c]) for c in result))
            
            # 验证唯一性
            values = list(solution.values())
            if len(values) != len(set(values)):
                return False
            
            return sum_terms == result_num
        except (KeyError, ValueError):
            return False
    
    # 其他额外方法

