import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class Koroperationunicodeffe1RewardCalculator(BaseRewardCalculator):
    """Koroperationunicodeffe1奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        case_type = identity.get('type', 'finite')
        correct = identity['solution']

        def normalize(s):
            s = re.sub(r'\s+', '', s).lower()
            s = s.replace('< =', '≤').replace('>=', '≥')
            s = s.replace('=<', '≤').replace('=>', '≥')
            return s

        if case_type == 'finite':
            try:
                elements = re.findall(r'[^,{}\s]+', solution)
                parsed = {int(e) if e.isdigit() else e for e in elements}
                return parsed == set(correct)
            except:
                return False
        else:
            return normalize(solution) == normalize(str(correct))
    
    # 其他额外方法

