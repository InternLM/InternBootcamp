import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
import math




class EoptimalpolygonperimeterRewardCalculator(BaseRewardCalculator):
    """Eoptimalpolygonperimeter奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            parts = list(map(int, matches[-1].strip().split()))
            return parts
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity["answers"]
        return solution == expected
    
    # 其他额外方法

