import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class KorlogiccooperativeprincipleRewardCalculator(BaseRewardCalculator):
    """Korlogiccooperativeprinciple奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[\[([ABC])\]\]', output, re.IGNORECASE)
        return matches[-1].upper() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return str(solution).upper() == identity['correct']
    
    # 其他额外方法

