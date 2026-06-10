import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CelementexterminationRewardCalculator(BaseRewardCalculator):
    """Celementextermination奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(YES|NO)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1].upper() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_answer']
    
    # 其他额外方法

