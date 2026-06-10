import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import math
import random
from math import gcd
from collections import defaultdict




class DrecoveringbstRewardCalculator(BaseRewardCalculator):
    """Drecoveringbst奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](Yes|No)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1].capitalize() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_answer']
    
    # 其他额外方法

