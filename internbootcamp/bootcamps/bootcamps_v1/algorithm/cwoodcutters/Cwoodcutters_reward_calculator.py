import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from copy import deepcopy




class CwoodcuttersRewardCalculator(BaseRewardCalculator):
    """Cwoodcutters奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answers = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(answers[-1]) if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return int(solution) == cls._compute_optimal(identity['trees'])
        except:
            return False
    
    # 其他额外方法

