import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EhelpingpeopleRewardCalculator(BaseRewardCalculator):
    """Ehelpingpeople奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r"\[answer\](.*?)\[/answer\]", output, re.DOTALL)
        if not matches:
            return None
        try:
            return float(matches[-1].strip().split()[0])
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        if solution is None:
            return False
        expected = case["correct_output"]
        abs_err = abs(solution - expected)
        if abs_err < 1e-6:
            return True
        if expected == 0:
            return abs_err == 0
        rel_err = abs_err / abs(expected)
        return rel_err < 1e-6
    
    # 其他额外方法

