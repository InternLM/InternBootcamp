import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random




class EnumbertransformationiiRewardCalculator(BaseRewardCalculator):
    """Enumbertransformationii奖励计算器"""
    
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
        answer_str = output[start + len(start_tag):end].strip()
        if answer_str.isdigit():
            return int(answer_str)
        else:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['a']
        b = identity['b']
        xi = identity['xi']
        expected = cls.compute_min_steps(a, b, xi)
        return solution == expected
    
    # 其他额外方法

