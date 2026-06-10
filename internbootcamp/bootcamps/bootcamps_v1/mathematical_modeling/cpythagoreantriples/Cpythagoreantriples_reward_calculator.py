import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CpythagoreantriplesRewardCalculator(BaseRewardCalculator):
    """Cpythagoreantriples奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        start_tag = "[answer]"
        end_tag = "[/answer]"
        start = output.rfind(start_tag)
        if start == -1:
            return None
        end = output.find(end_tag, start + len(start_tag))
        if end == -1:
            return None
        answer = output[start + len(start_tag):end].strip()
        if answer == "-1":
            return -1
        try:
            m, k = map(int, answer.split())
            return (m, k)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        if solution == -1:
            return identity.get('solution', None) == -1
        m, k = solution
        # Check if n is a leg
        if n**2 + m**2 == k**2:
            return True
        # Check if n is the hypotenuse
        if m**2 + k**2 == n**2 and cls.allow_hypotenuse:
            return True
        return False
    
    # 其他额外方法

