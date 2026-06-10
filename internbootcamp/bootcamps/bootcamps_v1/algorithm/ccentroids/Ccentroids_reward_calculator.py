import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CcentroidsRewardCalculator(BaseRewardCalculator):
    """Ccentroids奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        parts = last_match.split()
        try:
            solution = list(map(int, parts))
        except ValueError:
            return None
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct = identity['correct_answer']
        if not isinstance(solution, list):
            return False
        if len(solution) != len(correct):
            return False
        return solution == correct
    
    # 其他额外方法

