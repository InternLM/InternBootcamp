import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class DmissionimpassableRewardCalculator(BaseRewardCalculator):
    """Dmissionimpassable奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](-?\d+)\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            correct = cls._compute_max_score(identity)
            return int(solution) == correct
        except:
            return False
    
    # 其他额外方法

