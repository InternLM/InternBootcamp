import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import math
import random
from collections import defaultdict




class CinstantnoodlesRewardCalculator(BaseRewardCalculator):
    """Cinstantnoodles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[ANSWER\](.*?)\[/ANSWER\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_gcd']
    
    # 其他额外方法

