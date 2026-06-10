import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CtouristsnotesRewardCalculator(BaseRewardCalculator):
    """Ctouristsnotes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip().upper()  # Unified case handling
        if last_match == 'IMPOSSIBLE':
            return 'IMPOSSIBLE'
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct = identity['correct_answer']
        if isinstance(correct, int):
            return isinstance(solution, int) and solution == correct
        else:
            return solution == 'IMPOSSIBLE'
    
    # 其他额外方法

