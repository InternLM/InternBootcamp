import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class AexamsRewardCalculator(BaseRewardCalculator):
    """Aexams奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        exams = identity['exams']
        sorted_exams = sorted(exams, key=lambda x: (x[0], x[1]))
        ans = 0
        for a, b in sorted_exams:
            if ans <= b:
                ans = b
            else:
                ans = a
        return isinstance(solution, int) and solution == ans
    
    # 其他额外方法

