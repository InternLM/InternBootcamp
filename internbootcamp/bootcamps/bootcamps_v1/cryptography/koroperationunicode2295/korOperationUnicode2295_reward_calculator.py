import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class Koroperationunicode2295RewardCalculator(BaseRewardCalculator):
    """Koroperationunicode2295奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        return re.sub(r'\s+', '', last_match)  # 移除所有空格
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        def parse_complex(s):
            s = s.replace(' ', '').lower().replace('i', 'j')
            try:
                c = complex(s)
                return (round(c.real, 2), round(c.imag, 2))
            except:
                return (None, None)
        
        if identity['type'] == 'equation':
            try:
                user_value = round(float(solution), 2)
                return user_value == identity['solution']
            except:
                return False
        else:
            real, imag = parse_complex(solution)
            if real is None or imag is None:
                return False
            target_real = round(identity['solution_real'], 2)
            target_imag = round(identity['solution_imag'], 2)
            return (real == target_real) and (imag == target_imag)
    
    # 其他额外方法

