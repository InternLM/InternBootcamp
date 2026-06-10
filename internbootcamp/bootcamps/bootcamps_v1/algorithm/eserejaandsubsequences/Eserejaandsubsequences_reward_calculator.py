import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EserejaandsubsequencesRewardCalculator(BaseRewardCalculator):
    """Eserejaandsubsequences奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        digits = re.sub(r'\D', '', last_match)
        try:
            return int(digits) % (10**9 + 7)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct_answer = identity.get('answer')
        return solution == correct_answer
    
    # 其他额外方法

