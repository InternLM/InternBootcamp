import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CbuildingpermutationRewardCalculator(BaseRewardCalculator):
    """Cbuildingpermutation奖励计算器"""
    
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
        return answer_str
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        a = identity['a']
        a_sorted = sorted(a)
        target = list(range(1, n+1))
        expected = sum(abs(a_sorted[i] - target[i]) for i in range(n))
        try:
            return int(solution) == expected
        except ValueError:
            return False
    
    # 其他额外方法

