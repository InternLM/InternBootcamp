import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re




class KorpuzzlewordscapesRewardCalculator(BaseRewardCalculator):
    """Korpuzzlewordscapes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            last_match = matches[-1].strip()
            return [row.strip().split() for row in last_match.split(',')]
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = identity["__solution__"]
            return solution == expected
        except:
            return False
    
    # 其他额外方法

