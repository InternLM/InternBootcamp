import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CcivilizationRewardCalculator(BaseRewardCalculator):
    """Ccivilization奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output)
        if not matches:
            return None
        last_match = matches[-1]
        answers = last_match.split(',')
        try:
            answers = [int(a.strip()) for a in answers]
        except ValueError:
            return None
        return answers
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['results']
        if not solution or not isinstance(solution, list):
            return False
        if len(solution) != len(expected):
            return False
        for s, e in zip(solution, expected):
            if s != e:
                return False
        return True
    
    # 其他额外方法

