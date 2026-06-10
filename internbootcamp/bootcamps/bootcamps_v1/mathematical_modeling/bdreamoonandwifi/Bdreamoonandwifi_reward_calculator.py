import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math




class BdreamoonandwifiRewardCalculator(BaseRewardCalculator):
    """Bdreamoonandwifi奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](0?\.\d{12}|0|1\.0{12})\[/answer\]', output)
        try:
            return float(matches[-1]) if matches else None
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        try:
            return math.isclose(solution, case['_target'], rel_tol=1e-12, abs_tol=1e-12)
        except TypeError:
            return False
    
    # 其他额外方法

